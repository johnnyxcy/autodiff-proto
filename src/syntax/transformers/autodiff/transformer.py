from keyword import iskeyword
from token import NAME, OP
from typing import Any

import libcst as cst
from libcst.metadata import (
    ExpressionContextProvider,
    ParentNodeProvider,
)
from sympy import (
    Basic,
    Expr,
    Float,
    Function,
    Number,
    Symbol,
    parse_expr,
)
from sympy.assumptions.ask import AssumptionKeys
from sympy.parsing.sympy_parser import (
    DICT,
    TOKEN,
    auto_number,
    null,
    repeated_decimals,
)

from symbols._symvar import SymVar
from symbols._x import XWrt
from symbols.to_cst import parse_sympy_expr
from syntax.metadata.scope_provider import (
    Scope,
    ScopeProvider,
)
from syntax.rethrow import rethrow
from syntax.unparse import unparse
from syntax.with_comment import with_comment


def auto_symbol(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    """Inserts calls to ``Symbol``/``Function`` for undefined variables."""
    result: list[TOKEN] = []
    prevTok = (-1, "")

    tokens.append((-1, ""))  # so zip traverses all tokens
    for tok, nextTok in zip(tokens, tokens[1:]):
        tokNum, tokVal = tok
        nextTokNum, nextTokVal = nextTok
        if tokNum == NAME:
            name = tokVal

            if (
                name in ["True", "False", "None"]
                or iskeyword(name)
                # Don't convert attribute access
                or (prevTok[0] == OP and prevTok[1] == ".")
                # Don't convert keyword arguments
                or (
                    prevTok[0] == OP
                    and prevTok[1] in ("(", ",")
                    and nextTokNum == OP
                    and nextTokVal == "="
                )
                # the name has already been defined
                or name in local_dict
                and local_dict[name] is not null
            ):
                result.append((NAME, name))
                continue
            elif name in local_dict:
                local_dict.setdefault(null, set()).add(name)
                if nextTokVal == "(":
                    local_dict[name] = Function(name)
                else:
                    local_dict[name] = Symbol(name)
                result.append((NAME, name))
                continue
            elif name in global_dict:
                obj = global_dict[name]
                if isinstance(obj, (AssumptionKeys, Basic, type)) or callable(obj):
                    result.append((NAME, name))
                    continue

            if nextTokVal == "(":  # is a function call, we dont auto symbolize
                raise NameError(f"Function '{name}' is not defined.")

            result.extend(
                [
                    (NAME, "Symbol" if nextTokVal != "(" else "Function"),
                    (OP, "("),
                    (NAME, repr(str(name))),
                    (OP, ")"),
                ]
            )
        else:
            result.append((tokNum, tokVal))

        prevTok = (tokNum, tokVal)

    return result


AutoDiffMap = dict[str, dict[SymVar, Expr]]
ScopedAutoDiffMap = dict[Scope, AutoDiffMap]


class AutoDiffTransformer(cst.CSTTransformer):
    """
    A transformer that modifies the AST to support automatic differentiation.
    """

    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        ScopeProvider,
        ExpressionContextProvider,
    )

    def __init__(
        self,
        source_code: str,
        locals: dict[str, Any],
        globals: dict[str, Any],
        symbols: list[SymVar] | None = None,
        wrt: list[SymVar | tuple[SymVar, SymVar]] | None = None,
    ):
        self._source_code = source_code
        self._locals = locals
        self._globals = globals
        self._symbols = symbols or []
        self._wrt = wrt or []

        self._scoped_auto_diff: ScopedAutoDiffMap = {}

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine):
        if node.trailing_whitespace.comment:
            # If the statement has a comment, we need to check if it is a
            # special comment that we want to handle
            if node.trailing_whitespace.comment.value.strip().startswith(
                "# mtran: ignore"
            ):
                # This is a special comment, we need to handle it
                return False
        return super().visit_SimpleStatementLine(node)

    def visit_Assign(self, node: cst.Assign):
        scope = self.get_metadata(ScopeProvider, node, None)
        if scope is None:
            return super().visit_Assign(node)

        if scope not in self._scoped_auto_diff:
            self._scoped_auto_diff[scope] = {}

        targets = node.targets
        if len(targets) != 1:
            rethrow(
                SyntaxError("Only single assignment is supported"),
                node,
                source_code=self._source_code,
            )
        target = targets[0].target
        # handle name assignment
        if isinstance(target, cst.Name):
            target_name = target.value
            if target_name not in scope:
                rethrow(
                    NameError(f"Variable '{target_name}' is not defined"),
                    node,
                    source_code=self._source_code,
                )

            if target in self._scoped_auto_diff[scope]:
                rethrow(
                    SyntaxError(f"Variable '{target}' is already defined"),
                    node,
                    source_code=self._source_code,
                )
            self._scoped_auto_diff[scope][target.value] = {}

            # Evaluate the value of the assignment
            value = node.value
            evaluated_value = self._eval(value, scope=scope)

            if isinstance(evaluated_value, Expr):
                for wrt in self._wrt:
                    if isinstance(wrt, tuple):
                        wrt1st, wrt2nd = wrt
                    else:
                        wrt1st = wrt
                        wrt2nd = None
                    first_order_deriv = evaluated_value.diff(wrt)
                    for symbol in evaluated_value.free_symbols:
                        if (
                            isinstance(symbol, Symbol)
                            and symbol.name in scope.assignments
                        ):
                            s_ = (
                                self._scoped_auto_diff[scope]
                                .get(symbol.name, {})
                                .get(wrt1st, None)
                            )

                            if s_ is not None:
                                if isinstance(s_, Number):
                                    s_ = Float(s_)
                                else:
                                    s_ = XWrt(symbol.name, wrt1st)
                                first_order_deriv += evaluated_value.diff(symbol) * s_  # pyright: ignore[reportOperatorIssue]
                    if wrt2nd is not None:
                        raise NotImplementedError("TODO: handle 2nd order deriv")
                    self._scoped_auto_diff[scope][target.value][wrt1st] = (
                        first_order_deriv
                    )

        return super().visit_Assign(node)

    def _leave_Suite(self, suite: cst.BaseSuite) -> cst.BaseSuite:
        """
        Leave a suite node and return the updated node.
        """
        new_body: list[cst.BaseStatement] = []
        for stmt in cst.ensure_type(suite, cst.IndentedBlock).body:
            scope = self.get_metadata(ScopeProvider, stmt, None)
            if scope is None or scope not in self._scoped_auto_diff:
                new_body.append(stmt)
                continue
            auto_diff_x = self._scoped_auto_diff[scope]
            if isinstance(stmt, cst.SimpleStatementLine):
                if len(stmt.body) != 1:
                    rethrow(
                        SyntaxError("Only single statement is supported"),
                        stmt,
                        source_code=self._source_code,
                    )
                small_stmt = stmt.body[0]
                new_body.append(stmt)
                if isinstance(small_stmt, cst.Assign):
                    if len(small_stmt.targets) != 1:
                        rethrow(
                            SyntaxError("Only single assignment is supported"),
                            small_stmt,
                            source_code=self._source_code,
                        )
                    target = small_stmt.targets[0].target
                    if isinstance(target, cst.Name):
                        for symvar, expr in auto_diff_x.get(target.value, {}).items():
                            assign_ = cst.Assign(
                                targets=[
                                    cst.AssignTarget(
                                        target=XWrt(target.value, symvar).as_cst()
                                    )
                                ],
                                value=parse_sympy_expr(expr=expr),
                            )
                            new_body.append(
                                with_comment(
                                    cst.SimpleStatementLine(
                                        body=[assign_],
                                    ),
                                    comment=f"# {target.value} wrt {symvar.name}",
                                )
                            )
            elif isinstance(stmt, cst.If):
                if_scope = self.get_metadata(ScopeProvider, stmt.body, None)
                updated_stmt = stmt.with_changes(
                    body=self._leave_Suite(stmt.body),
                )

                if stmt.orelse:
                    else_scope = self.get_metadata(ScopeProvider, stmt.orelse, None)
                    updated_stmt = updated_stmt.with_changes(
                        orelse=stmt.orelse.with_changes(
                            body=self._leave_Suite(stmt.orelse.body),
                        )
                    )

                    if if_scope is not None and else_scope is not None:
                        if_scope_assignment_names = [
                            ass.name for ass in if_scope.assignments
                        ]
                        else_scope_assignment_names = [
                            ass.name for ass in else_scope.assignments
                        ]

                        branched_assignment_names = set(
                            if_scope_assignment_names
                        ).intersection(else_scope_assignment_names)

                        for branch_assignment_name in branched_assignment_names:
                            for symbol in self._symbols:
                                if branch_assignment_name not in auto_diff_x:
                                    auto_diff_x[branch_assignment_name] = {}
                                auto_diff_x[branch_assignment_name][symbol] = XWrt(
                                    branch_assignment_name, wrt=symbol
                                )

                new_body.append(updated_stmt)
        return suite.with_changes(body=new_body)

    def visit_If(self, node: cst.If):
        parent_scope = self.get_metadata(ScopeProvider, node, None)
        if parent_scope is None:
            return super().visit_If(node)
        if parent_scope not in self._scoped_auto_diff:
            self._scoped_auto_diff[parent_scope] = {}
        auto_diff_x = self._scoped_auto_diff[parent_scope]
        if_scope = self.get_metadata(ScopeProvider, node.body, None)

        if node.orelse:
            else_scope = self.get_metadata(ScopeProvider, node.orelse, None)

            if if_scope is not None and else_scope is not None:
                if_scope_assignment_names = [ass.name for ass in if_scope.assignments]
                else_scope_assignment_names = [
                    ass.name for ass in else_scope.assignments
                ]

                branched_assignment_names = set(if_scope_assignment_names).intersection(
                    else_scope_assignment_names
                )

                for branch_assignment_name in branched_assignment_names:
                    for symbol in self._symbols:
                        if branch_assignment_name not in auto_diff_x:
                            auto_diff_x[branch_assignment_name] = {}
                        auto_diff_x[branch_assignment_name][symbol] = XWrt(
                            branch_assignment_name, wrt=symbol
                        )

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        return updated_node.with_changes(body=self._leave_Suite(original_node.body))

    def _eval(self, token: cst.CSTNode, scope: Scope) -> Any:
        """
        Evaluate a token in the context of the given locals and globals.

        Args:
            token (cst.CSTNode): The CST token to evaluate.
            scope (Scope): The scope in which to evaluate the token.

        Returns:
            Any: The result of the evaluation.
        """
        expr = unparse(token)

        try:
            parsed = parse_expr(
                expr,
                transformations=(
                    auto_number,
                    auto_symbol,
                    repeated_decimals,
                ),
                local_dict=self._locals,
            )

        except Exception as e:
            rethrow(
                e,
                token,
                source_code=self._source_code,
            )
        if isinstance(parsed, Expr):
            for symbol in parsed.free_symbols:
                if symbol in self._symbols:
                    continue

                if isinstance(symbol, Symbol):
                    name = symbol.name

                    if name not in scope:
                        rethrow(
                            NameError(f"Variable '{name}' is used before definition"),
                            token,
                            source_code=self._source_code,
                        )
        return parsed
