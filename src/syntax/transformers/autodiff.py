from dataclasses import dataclass
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
    Function,
    Symbol,
    cse,
    numbered_symbols,
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

from symbols._ns import SymbolDefs
from symbols._ode import CmtDADt
from symbols._x import X, XWrt
from symbols._y import Y, YTypeLiteral, YWrt
from symbols.sympy_parser import parse_sympy_expr
from syntax.metadata.scope_provider import (
    Scope,
    ScopeProvider,
)
from syntax.rethrow import rethrow
from syntax.unparse import unparse
from syntax.with_comment import with_comment

__all__ = ["AutoDiffTransformer"]


@dataclass(kw_only=True)
class FirstOrderDerivativeInfo:
    """
    A dataclass to hold information about first order derivatives.
    """

    expr: Expr
    wrt: Symbol


@dataclass(kw_only=True)
class XFirstOrderDerivativeInfo(FirstOrderDerivativeInfo):
    """
    A dataclass to hold information about first order derivatives.
    """

    x_name: str

    @property
    def as_assign_target_expression(self):
        """
        Get the assign target for the first order derivative.
        """
        return cst.ensure_type(
            XWrt(self.x_name, self.wrt).as_cst_expression(),
            cst.BaseAssignTargetExpression,
        )


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


AutoDiffMap = dict[X | CmtDADt, dict[Symbol, Expr]]
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
        symbol_defs: SymbolDefs | None = None,
    ):
        self._source_code = source_code
        self._locals = locals
        self._globals = globals
        self._symbol_defs = symbol_defs or SymbolDefs()

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

    def _do_autodiff_and_cse(
        self, value: Expr, scope: Scope
    ) -> tuple[list[cst.BaseStatement], list[tuple[Symbol, Expr]]]:
        first_order_derivatives: list[tuple[Symbol, Expr]] = []

        if isinstance(value, Expr) and not value.is_constant():
            for wrt in self._symbol_defs.iter_eta():
                first_order_deriv = value.diff(wrt)
                for symbol in value.free_symbols:
                    if isinstance(symbol, Symbol) and symbol.name in scope:
                        first_order_deriv += value.diff(symbol) * XWrt(symbol.name, wrt)
                first_order_derivatives.append((wrt, first_order_deriv))

        replacements, reductions = cse(
            exprs=[expr for _, expr in first_order_derivatives],
            symbols=numbered_symbols(prefix="__"),
            list=True,
        )
        if not isinstance(reductions, list):
            raise NotImplementedError()
        sub_expr_term: Symbol
        sub_expr: Expr
        replacement_assignments: list[cst.BaseStatement] = []
        for sub_expr_term, sub_expr in replacements:
            replacement_assignments.append(
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(target=cst.Name(sub_expr_term.name))
                            ],
                            value=parse_sympy_expr(sub_expr),
                        )
                    ]
                )
            )

        for i, reduced_expr in enumerate(reductions):
            first_order_derivatives[i] = (first_order_derivatives[i][0], reduced_expr)

        return replacement_assignments, first_order_derivatives

    def _autodiff_transform_assign(
        self, assign: cst.Assign, scope: Scope
    ) -> list[cst.BaseStatement]:
        """
        Handle the assignment node for automatic differentiation.
        This method is called when an assignment is encountered.
        """
        targets = assign.targets
        if len(targets) != 1:
            rethrow(
                SyntaxError("Only single assignment is supported"),
                assign,
                source_code=self._source_code,
            )
        target = targets[0].target
        # Evaluate the value of the assignment
        value = assign.value
        evaluated_value = self._eval(value, scope=scope)

        first_order_body: list[cst.BaseStatement] = []
        if isinstance(evaluated_value, Expr) and not evaluated_value.is_constant():
            if isinstance(target, cst.Name):
                replacement_assignments, derivatives = self._do_autodiff_and_cse(
                    value=evaluated_value, scope=scope
                )
                first_order_body.extend(replacement_assignments)
                for wrt, expr in derivatives:
                    first_order_body.append(
                        with_comment(
                            cst.SimpleStatementLine(
                                body=[
                                    cst.Assign(
                                        targets=[
                                            cst.AssignTarget(
                                                target=cst.ensure_type(
                                                    XWrt(
                                                        target.value, wrt
                                                    ).as_cst_expression(),
                                                    cst.BaseAssignTargetExpression,
                                                )
                                            )
                                        ],
                                        value=parse_sympy_expr(expr),
                                    )
                                ],
                            ),
                            comment=f"# mtran: {target.value} wrt {wrt.name}",
                        )
                    )

        transformed: list[cst.BaseStatement] = []
        if len(first_order_body) > 0:
            transformed.append(
                cst.If(
                    test=cst.Name("__FIRST_ORDER"),
                    body=cst.IndentedBlock(body=first_order_body),
                )
            )
        return transformed

    def _autodiff_transform_return(
        self, return_: cst.Return, scope: Scope
    ) -> list[cst.BaseStatement]:
        """
        Handle the return node for automatic differentiation.
        This method is called when a return statement is encountered.
        """
        value = return_.value
        if value is None:
            rethrow(
                SyntaxError(
                    "Return statement must return an expression. For example, use `return IPRED` instead of `return`"
                ),
                return_,
                source_code=self._source_code,
            )
        evaluated_value = self._eval(value, scope=scope)
        transformed: list[cst.BaseStatement] = []
        y_type: YTypeLiteral = "prediction"
        if isinstance(evaluated_value, Y):
            y_type = evaluated_value.type

        transformed.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[
                            cst.AssignTarget(target=Y(y_type).as_cst_expression())
                        ],
                        value=parse_sympy_expr(evaluated_value),
                    )
                ]
            )
        )

        first_order_body: list[cst.BaseStatement] = []
        if isinstance(evaluated_value, Expr) and not evaluated_value.is_constant():
            replacement_assignments, derivatives = self._do_autodiff_and_cse(
                value=evaluated_value, scope=scope
            )
            first_order_body.extend(replacement_assignments)
            for wrt, expr in derivatives:
                first_order_body.append(
                    with_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                YWrt(wrt).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: __Y__ wrt {wrt.name}",
                    )
                )

        if len(first_order_body) > 0:
            transformed.append(
                cst.If(
                    test=cst.Name("__FIRST_ORDER"),
                    body=cst.IndentedBlock(body=first_order_body),
                )
            )
        transformed.append(cst.SimpleStatementLine(body=[cst.Return()]))
        return transformed

    def _autodiff_transform_If(
        self, if_: cst.If, scope: Scope
    ) -> list[cst.BaseStatement]:
        """
        Handle the if statement for automatic differentiation.
        This method is called when an if statement is encountered.
        """
        transformed: list[cst.BaseStatement] = []
        updated_stmt = if_.with_changes(
            body=self._transform_Suite(if_.body),
        )

        if if_.orelse:
            updated_stmt = updated_stmt.with_changes(
                orelse=if_.orelse.with_changes(
                    body=self._transform_Suite(if_.orelse.body),
                )
            )
            transformed.append(updated_stmt)
        else:
            transformed.append(updated_stmt)

        return transformed

    def _transform_Suite(self, suite: cst.BaseSuite) -> cst.BaseSuite:
        """
        Leave a suite node and return the updated node.
        """
        new_body: list[cst.BaseStatement] = []
        for stmt in cst.ensure_type(suite, cst.IndentedBlock).body:
            scope = self.get_metadata(ScopeProvider, stmt, None)
            if scope is None:
                new_body.append(stmt)
                continue
            if isinstance(stmt, cst.SimpleStatementLine):
                if len(stmt.body) != 1:
                    rethrow(
                        SyntaxError("Only single statement is supported"),
                        stmt,
                        source_code=self._source_code,
                    )
                small_stmt = stmt.body[0]
                if isinstance(small_stmt, cst.Assign):
                    new_body.append(stmt)
                    new_body.extend(
                        self._autodiff_transform_assign(small_stmt, scope=scope)
                    )
                elif isinstance(small_stmt, cst.Return):
                    new_body.extend(
                        self._autodiff_transform_return(small_stmt, scope=scope)
                    )
                else:
                    rethrow(
                        NotImplementedError(
                            f'Cannot handle "{type(small_stmt).__name__}" statement yet'
                        ),
                        stmt,
                        source_code=self._source_code,
                    )
            elif isinstance(stmt, cst.If):
                new_body.extend(self._autodiff_transform_If(stmt, scope))
        return suite.with_changes(body=new_body)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        return updated_node.with_changes(body=self._transform_Suite(original_node.body))

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
                if self._symbol_defs.has_symbol(symbol):
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
