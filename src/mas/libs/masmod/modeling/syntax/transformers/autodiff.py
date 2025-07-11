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
    Number,
    Symbol,
    cse,
    numbered_symbols,
    parse_expr,
)
from sympy.assumptions.ask import AssumptionKeys
from sympy.parsing.sympy_parser import (
    DICT,
    TOKEN,
    null,
)

from mas.libs.masmod.modeling.module.closed_form_solutions._args import (
    ParamKwargs,
    get_args_of_solution,
)
from mas.libs.masmod.modeling.module.defs.closed_form import (
    ClosedFormSolutionModule,
    get_annotated_meta,
)
from mas.libs.masmod.modeling.module.defs.module import Module
from mas.libs.masmod.modeling.module.defs.ode import OdeModule
from mas.libs.masmod.modeling.symbols._closed_form import (
    ClosedFormSolutionSolvedA,
    ClosedFormSolutionSolvedAWrt,
    ClosedFormSolutionSolvedF,
    ClosedFormSolutionSolvedFWrt,
    ClosedFormSolveCall,
)
from mas.libs.masmod.modeling.symbols._cmt import (
    CmtDADt,
    CmtDADtWrt,
    CmtDosingParamSymbol,
    CmtSolvedA,
    CmtSolvedAWrt,
)
from mas.libs.masmod.modeling.symbols._ns import SymbolNamespace
from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps
from mas.libs.masmod.modeling.symbols._x import XWrt
from mas.libs.masmod.modeling.symbols._y import Y, YType, YValue, YWrt
from mas.libs.masmod.modeling.symbols.sympy_parser import parse_sympy_expr
from mas.libs.masmod.modeling.syntax.metadata.scope_provider import (
    Scope,
    ScopeProvider,
)
from mas.libs.masmod.modeling.syntax.rethrow import rethrow
from mas.libs.masmod.modeling.syntax.unparse import unparse
from mas.libs.masmod.modeling.syntax.with_comment import with_trailing_comment

__all__ = ["AutoDiffTransformer"]

FIRST_ORDER = Symbol("__FIRST_ORDER")
SECOND_ORDER = Symbol("__SECOND_ORDER")


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


# tuple[list[cst.BaseStatement], list[tuple[Symbol, Expr]]]
FirstOrderDerivative = tuple[Eta | Eps | CmtSolvedA, Expr]
SecondOrderDerivative = tuple[tuple[Eta, Eta | Eps], Expr]


@dataclass(frozen=True)
class ReducedDerivatives:
    cse_stmts: list[cst.BaseStatement]
    first_order: list[FirstOrderDerivative]
    second_order: list[SecondOrderDerivative]


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
        module_cls: type[Module] = Module,
        symbol_defs: SymbolNamespace | None = None,
    ):
        self._source_code = source_code
        self._locals = locals
        self._globals = globals
        self._module_cls = module_cls
        self._symbol_defs = symbol_defs or SymbolNamespace()

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

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        return updated_node.with_changes(body=self._transform_Suite(original_node.body))

    def _do_autodiff_and_cse(
        self,
        value: Expr | float | int,
        scope: Scope,
        wrt_etas: bool = True,
        wrt_eps: bool = True,
    ) -> ReducedDerivatives:
        first_order_derivatives: list[FirstOrderDerivative] = []
        second_order_derivatives: list[SecondOrderDerivative] = []

        if isinstance(value, Expr):
            wrt_symbols: list[Eta | Eps] = []
            if wrt_etas:
                wrt_symbols.extend(self._symbol_defs.iter_eta())
            if wrt_eps:
                wrt_symbols.extend(self._symbol_defs.iter_eps())

            for i, wrt in enumerate(wrt_symbols):
                # Z wrt η/ε
                value_wrt_var = value.diff(wrt)

                if isinstance(wrt, Eta):
                    # Only chained when wrt is η
                    if issubclass(self._module_cls, OdeModule):
                        # chained 1a, ∂Z/∂A(i) * ∂A(i)/∂η
                        for cmt in self._symbol_defs.iter_cmt():
                            value_wrt_var += value.diff(cmt.A) * CmtSolvedAWrt(
                                cmt=cmt, wrt=wrt
                            )
                    elif issubclass(self._module_cls, ClosedFormSolutionModule):
                        # chained 1b, ∂Z/∂F * ∂F/∂η
                        value_wrt_var += value.diff(
                            ClosedFormSolutionSolvedF()
                        ) * ClosedFormSolutionSolvedFWrt(wrt=wrt)
                        n_cmt = get_annotated_meta(self._module_cls).n_cmt
                        for cmt_index in range(n_cmt):
                            # chained 1c, ∂Z/∂A(i) * ∂A(i)/∂η
                            value_wrt_var += value.diff(
                                ClosedFormSolutionSolvedA(index=cmt_index)
                            ) * ClosedFormSolutionSolvedAWrt(index=cmt_index, wrt=wrt)

                # chained arbitrary symbols
                for symbol in value.free_symbols:
                    if isinstance(symbol, Symbol) and symbol.name in scope:
                        # Z wrt x
                        value_wrt_x = value.diff(symbol)
                        # chained 2a, ∂Z/∂x * ∂x/∂η(ε)
                        value_wrt_var += value_wrt_x * XWrt(symbol.name, wrt)
                        if isinstance(wrt, Eta):
                            if issubclass(self._module_cls, OdeModule):
                                for cmt in self._symbol_defs.iter_cmt():
                                    # chained 2b, ∂Z/∂x * ∂x/∂A(i) * ∂A(i)/∂η
                                    value_wrt_var += (
                                        value_wrt_x
                                        * XWrt(symbol.name, cmt.A)
                                        * CmtSolvedAWrt(cmt=cmt, wrt=wrt)
                                    )

                first_order_derivatives.append((wrt, value_wrt_var))

                for j, wrt2nd in enumerate(wrt_symbols):
                    if isinstance(wrt, Eta):
                        deriv_2nd = None
                        # ∂²Z/∂ηᵢ∂ηⱼ
                        if isinstance(wrt2nd, Eta):
                            # since it is symmetric, we only compute the lower triangle
                            if i < j:
                                continue
                            if issubclass(self._module_cls, OdeModule):
                                deriv_2nd = (
                                    self._compute_ode_value_2nd_mixed_partial_deriv(
                                        value=value,
                                        wrt=wrt,
                                        wrt2nd=wrt2nd,
                                        scope=scope,
                                    )
                                )
                            elif issubclass(self._module_cls, ClosedFormSolutionModule):
                                deriv_2nd = self._compute_closed_form_value_2nd_mixed_partial_deriv(
                                    value=value,
                                    wrt=wrt,
                                    wrt2nd=wrt2nd,
                                    scope=scope,
                                )
                        # ∂²Z/∂∂ηᵢ∂εⱼ
                        elif isinstance(wrt2nd, Eps):
                            deriv_2nd = value_wrt_var.diff(wrt2nd)
                            for symbol in value.free_symbols:
                                if isinstance(symbol, Symbol) and symbol.name in scope:
                                    deriv_2nd += value_wrt_var.diff(symbol) * XWrt(
                                        symbol.name, wrt2nd
                                    )

                        if deriv_2nd is not None:
                            second_order_derivatives.append(
                                (
                                    (wrt, wrt2nd),
                                    deriv_2nd,
                                )
                            )

            # if Ode, we also need to compute derivatives w.r.t. A(i)
            if issubclass(self._module_cls, OdeModule):
                for cmt in self._symbol_defs.iter_cmt():
                    # Z wrt A(i)
                    value_wrt_Ai = value.diff(cmt.A)
                    for symbol in value.free_symbols:
                        if isinstance(symbol, Symbol) and symbol.name in scope:
                            # chained, ∂Z/∂x * ∂x/∂A(i)
                            value_wrt_Ai += value.diff(symbol) * XWrt(
                                symbol.name, cmt.A
                            )
                    first_order_derivatives.append((cmt.A, value_wrt_Ai))

        # Perform common subexpression elimination (CSE) on the first order derivatives
        replacements, reductions = cse(
            exprs=[
                expr
                for _, expr in [*first_order_derivatives, *second_order_derivatives]
            ],
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

        # Update the derivatives with the reduced expressions
        i = 0
        for ii in range(len(first_order_derivatives)):
            first_order_derivatives[ii] = (
                first_order_derivatives[ii][0],
                reductions[i],
            )
            i += 1
        for jj in range(len(second_order_derivatives)):
            second_order_derivatives[jj] = (
                second_order_derivatives[jj][0],
                reductions[i],
            )
            i += 1

        return ReducedDerivatives(
            cse_stmts=replacement_assignments,
            first_order=first_order_derivatives,
            second_order=second_order_derivatives,
        )

    def _autodiff_arbitrary_x(
        self, x_name: str, value: Expr, scope: Scope
    ) -> list[cst.BaseStatement]:
        stmts: list[cst.BaseStatement] = []
        derivatives = self._do_autodiff_and_cse(value=value, scope=scope)
        stmts.extend(derivatives.cse_stmts)
        for wrt, expr in derivatives.first_order:
            stmts.append(
                with_trailing_comment(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[
                                    cst.AssignTarget(
                                        target=cst.ensure_type(
                                            XWrt(x_name, wrt).as_cst_expression(),
                                            cst.BaseAssignTargetExpression,
                                        )
                                    )
                                ],
                                value=parse_sympy_expr(expr),
                            )
                        ],
                    ),
                    comment=f"# mtran: {x_name} wrt {wrt.name}",
                )
            )
        second_order_body: list[cst.BaseStatement] = []
        for (wrt, wrt2nd), expr in derivatives.second_order:
            if isinstance(wrt, Eta) and isinstance(wrt2nd, Eps):
                # ∂²Z/∂εᵢ∂ηⱼ should be compute on __FIRST_ORDER
                parent = stmts
            else:
                parent = second_order_body
            parent.append(
                with_trailing_comment(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[
                                    cst.AssignTarget(
                                        target=cst.ensure_type(
                                            XWrt(
                                                x_name, wrt, wrt2nd
                                            ).as_cst_expression(),
                                            cst.BaseAssignTargetExpression,
                                        )
                                    )
                                ],
                                value=parse_sympy_expr(expr),
                            )
                        ],
                    ),
                    comment=f"# mtran: {x_name} wrt {wrt.name}, {wrt2nd.name}",
                )
            )
        stmts.append(
            cst.If(
                test=cst.Name(SECOND_ORDER.name),
                body=cst.IndentedBlock(body=second_order_body),
            )
        )
        return stmts

    def _autodiff_dAdt(
        self, dAdt: CmtDADt, value: Expr, scope: Scope
    ) -> list[cst.BaseStatement]:
        stmts: list[cst.BaseStatement] = []
        derivatives = self._do_autodiff_and_cse(value=value, scope=scope, wrt_eps=False)
        stmts.extend(derivatives.cse_stmts)
        for wrt, expr in derivatives.first_order:
            stmts.append(
                with_trailing_comment(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[
                                    cst.AssignTarget(
                                        target=cst.ensure_type(
                                            CmtDADtWrt(
                                                cmt=dAdt.cmt,
                                                wrt=wrt,
                                            ).as_cst_expression(),
                                            cst.BaseAssignTargetExpression,
                                        )
                                    )
                                ],
                                value=parse_sympy_expr(expr),
                            )
                        ],
                    ),
                    comment=f"# mtran: {dAdt.name} wrt {wrt.name}",
                )
            )
        second_order_body: list[cst.BaseStatement] = []
        for (wrt, wrt2nd), expr in derivatives.second_order:
            if isinstance(wrt2nd, Eps):
                # ∂²Z/∂∂ηᵢ∂εⱼ makes no sense here, we skip it
                continue
            second_order_body.append(
                with_trailing_comment(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[
                                    cst.AssignTarget(
                                        target=cst.ensure_type(
                                            CmtDADtWrt(
                                                cmt=dAdt.cmt,
                                                wrt=wrt,
                                                wrt2nd=wrt2nd,
                                            ).as_cst_expression(),
                                            cst.BaseAssignTargetExpression,
                                        )
                                    )
                                ],
                                value=parse_sympy_expr(expr),
                            )
                        ],
                    ),
                    comment=f"# mtran: {dAdt.name} wrt {wrt.name}, {wrt2nd.name}",
                )
            )

        stmts.append(
            cst.If(
                test=cst.Name(SECOND_ORDER.name),
                body=cst.IndentedBlock(body=second_order_body),
            )
        )
        return stmts

    def _autodiff_closed_form_solve_args(
        self, args: ParamKwargs, scope: Scope
    ) -> list[cst.BaseStatement]:
        stmts: list[cst.BaseStatement] = []

        for arg, expr in args.items():
            if expr is None:
                continue
            stmts.append(
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(
                                    target=cst.ensure_type(
                                        arg.as_cst_expression(),
                                        cst.BaseAssignTargetExpression,
                                    )
                                )
                            ],
                            value=parse_sympy_expr(expr),
                        )
                    ]
                )
            )

            derivatives = self._do_autodiff_and_cse(
                value=expr, scope=scope, wrt_eps=False
            )

            stmts.extend(derivatives.cse_stmts)

            first_order_body: list[cst.BaseStatement] = []
            for wrt, expr in derivatives.first_order:
                first_order_body.append(
                    with_trailing_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                arg.diff(wrt).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: {arg.param_name} wrt {wrt.name}",
                    )
                )

            second_order_body: list[cst.BaseStatement] = []
            for (wrt, wrt2nd), expr in derivatives.second_order:
                if isinstance(wrt2nd, Eps):
                    # ∂²Z/∂∂ηᵢ∂εⱼ makes no sense here, we skip it
                    continue
                second_order_body.append(
                    with_trailing_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                arg.diff(
                                                    wrt, wrt2nd
                                                ).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: {arg.param_name} wrt {wrt.name}, {wrt2nd.name}",
                    )
                )
            first_order_body.append(
                cst.If(
                    test=cst.Name(SECOND_ORDER.name),
                    body=cst.IndentedBlock(body=second_order_body),
                )
            )

            stmts.append(
                cst.If(
                    test=cst.Name(FIRST_ORDER.name),
                    body=cst.IndentedBlock(body=first_order_body),
                )
            )
        return stmts

    def _autodiff_cmt_dose_args(
        self, args: ParamKwargs, scope: Scope
    ) -> list[cst.BaseStatement]:
        stmts: list[cst.BaseStatement] = []

        for arg, expr in args.items():
            if expr is None:
                continue
            stmts.append(
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(
                                    target=cst.ensure_type(
                                        arg.as_cst_expression(),
                                        cst.BaseAssignTargetExpression,
                                    )
                                )
                            ],
                            value=parse_sympy_expr(expr),
                        )
                    ]
                )
            )

            derivatives = self._do_autodiff_and_cse(
                value=expr, scope=scope, wrt_eps=False
            )

            stmts.extend(derivatives.cse_stmts)
            first_order_body: list[cst.BaseStatement] = []
            for wrt, expr in derivatives.first_order:
                first_order_body.append(
                    with_trailing_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                arg.diff(wrt).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: {arg.param_name} wrt {wrt.name}",
                    )
                )

            second_order_body: list[cst.BaseStatement] = []
            for (wrt, wrt2nd), expr in derivatives.second_order:
                if isinstance(wrt2nd, Eps):
                    # ∂²Z/∂∂ηᵢ∂εⱼ makes no sense here, we skip it
                    continue
                second_order_body.append(
                    with_trailing_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                arg.diff(
                                                    wrt, wrt2nd
                                                ).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: {arg.param_name} wrt {wrt.name}, {wrt2nd.name}",
                    )
                )
            first_order_body.append(
                cst.If(
                    test=cst.Name(SECOND_ORDER.name),
                    body=cst.IndentedBlock(body=second_order_body),
                )
            )
            stmts.append(
                cst.If(
                    test=cst.Name(FIRST_ORDER.name),
                    body=cst.IndentedBlock(body=first_order_body),
                )
            )
        return stmts

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
        transformed: list[cst.BaseStatement] = []
        first_order_body: list[cst.BaseStatement] = []
        if isinstance(evaluated_value, ClosedFormSolutionSolvedF):
            transformed.extend(
                self._autodiff_closed_form_solve_args(
                    get_args_of_solution(evaluated_value), scope
                )
            )
            transformed.append(
                cst.SimpleStatementLine(
                    body=[cst.Expr(cst.Call(cst.Name(ClosedFormSolveCall.name)))]
                ),
            )
            if isinstance(target, cst.Name):
                transformed.append(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=targets,
                                value=ClosedFormSolutionSolvedF().as_cst_expression(),
                            )
                        ]
                    ),
                )
                first_order_body.extend(
                    self._autodiff_arbitrary_x(
                        x_name=target.value, value=evaluated_value, scope=scope
                    )
                )
            else:
                rethrow(
                    SyntaxError("Invalid solve assignment target"),
                    assign,
                    source_code=self._source_code,
                )
        elif isinstance(evaluated_value, Expr | float | int):
            if isinstance(evaluated_value, YValue):
                rethrow(
                    SyntaxError("Always use `return` for `likelihood`"),
                    assign,
                    self._source_code,
                )
            if isinstance(target, cst.Name):
                transformed.append(cst.SimpleStatementLine(body=[assign]))
                if isinstance(evaluated_value, Expr):
                    first_order_body.extend(
                        self._autodiff_arbitrary_x(
                            x_name=target.value, value=evaluated_value, scope=scope
                        )
                    )
            elif isinstance(target, cst.Attribute):
                attr = self._eval(target, scope=scope)

                if isinstance(attr, CmtDADt):
                    transformed.append(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                attr.as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=assign.value,
                                )
                            ]
                        )
                    )
                    if isinstance(evaluated_value, Expr):
                        first_order_body.extend(
                            self._autodiff_dAdt(
                                dAdt=attr, value=evaluated_value, scope=scope
                            )
                        )
                elif isinstance(attr, CmtDosingParamSymbol):
                    param_arg = attr.as_param_arg()

                    if isinstance(evaluated_value, Expr):
                        transformed.extend(
                            self._autodiff_cmt_dose_args(
                                args={param_arg: evaluated_value}, scope=scope
                            )
                        )
                    else:
                        transformed.append(
                            cst.SimpleStatementLine(
                                body=[
                                    cst.Assign(
                                        targets=[
                                            cst.AssignTarget(
                                                target=cst.ensure_type(
                                                    param_arg.as_cst_expression(),
                                                    cst.BaseAssignTargetExpression,
                                                )
                                            )
                                        ],
                                        value=assign.value,
                                    )
                                ]
                            )
                        )
                else:
                    rethrow(
                        ValueError("Invalid assignment target"),
                        assign,
                        source_code=self._source_code,
                    )

        if len(first_order_body) > 0:
            transformed.append(
                cst.If(
                    test=cst.Name(FIRST_ORDER.name),
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
        if isinstance(evaluated_value, ClosedFormSolutionSolvedF):
            transformed.extend(
                self._autodiff_closed_form_solve_args(
                    get_args_of_solution(evaluated_value), scope
                )
            )
            transformed.append(
                cst.SimpleStatementLine(
                    body=[cst.Expr(cst.Call(cst.Name("__solve__")))]
                )
            )

        y_type = 0
        if isinstance(evaluated_value, YValue):
            y_type = evaluated_value.flag
            evaluated_value = evaluated_value.expr

        transformed.extend(
            [
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(target=YType().as_cst_expression())
                            ],
                            value=cst.Integer(value=str(y_type)),
                        )
                    ]
                ),
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[cst.AssignTarget(target=Y().as_cst_expression())],
                            value=parse_sympy_expr(evaluated_value),
                        )
                    ]
                ),
            ]
        )

        first_order_body: list[cst.BaseStatement] = []
        if isinstance(evaluated_value, Expr):
            derivatives = self._do_autodiff_and_cse(value=evaluated_value, scope=scope)
            first_order_body.extend(derivatives.cse_stmts)
            for wrt, expr in derivatives.first_order:
                first_order_body.append(
                    with_trailing_comment(
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
            second_order_body: list[cst.BaseStatement] = []
            for (wrt, wrt2nd), expr in derivatives.second_order:
                if isinstance(wrt, Eta) and isinstance(wrt2nd, Eps):
                    # ∂²Z/∂εᵢ∂ηⱼ should be compute on __FIRST_ORDER
                    parent = first_order_body
                else:
                    parent = second_order_body

                parent.append(
                    with_trailing_comment(
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[
                                        cst.AssignTarget(
                                            target=cst.ensure_type(
                                                YWrt(wrt, wrt2nd).as_cst_expression(),
                                                cst.BaseAssignTargetExpression,
                                            )
                                        )
                                    ],
                                    value=parse_sympy_expr(expr),
                                )
                            ],
                        ),
                        comment=f"# mtran: __Y__ wrt {wrt.name}, {wrt2nd.name}",
                    )
                )
            first_order_body.append(
                cst.If(
                    test=cst.Name(SECOND_ORDER.name),
                    body=cst.IndentedBlock(body=second_order_body),
                )
            )

        transformed.append(
            cst.If(
                test=cst.Name(FIRST_ORDER.name),
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
                    new_body.extend(
                        self._autodiff_transform_assign(small_stmt, scope=scope)
                    )
                elif isinstance(small_stmt, cst.Return):
                    new_body.extend(
                        self._autodiff_transform_return(small_stmt, scope=scope)
                    )
                elif isinstance(small_stmt, cst.Expr):  # call
                    new_body.append(stmt)
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

    def _compute_ode_value_2nd_mixed_partial_deriv(
        self,
        value: Expr,
        wrt: Eta,
        wrt2nd: Eta,
        scope: Scope,
    ) -> Expr:
        """

        Formula:
            zᵤᵥ = yᵤᵥ
                + Σᵢ₌₁ᵐ (yᵤAᵢ·Aᵢᵥ + yᵥAᵢ·Aᵢᵤ)
                + Σᵢ₌₁ᵐ Σⱼ₌₁ᵐ yAⱼAᵢ·Aⱼᵤ·Aᵢᵥ
                + Σᵢ₌₁ᵐ yAᵢ·Aᵢᵤᵥ

        Where:
            • yᵤ, yᵥ           = ∂y/∂u, ∂y/∂v
            • yᵤAᵢ, yᵥAᵢ       = ∂²y/∂u∂Aᵢ, ∂²y/∂v∂Aᵢ
            • yAⱼAᵢ            = ∂²y/∂Aⱼ∂Aᵢ
            • Aᵢᵤ, Aᵢᵥ, Aᵢᵤᵥ   = ∂Aᵢ/∂u, ∂Aᵢ/∂v, ∂²Aᵢ/∂v∂u
        """
        if not issubclass(self._module_cls, OdeModule):
            return Number(0)
        yuv = value.diff(wrt, wrt2nd)
        zuv = yuv
        for cmt1 in self._symbol_defs.iter_cmt():
            yuAi = value.diff(wrt, cmt1.A)
            yvAi = value.diff(wrt2nd, cmt1.A)
            Aiu = CmtSolvedAWrt(cmt=cmt1, wrt=wrt)
            Aiv = CmtSolvedAWrt(cmt=cmt1, wrt=wrt2nd)
            yAi = value.diff(cmt1.A)
            Aiuv = CmtSolvedAWrt(cmt=cmt1, wrt=wrt, wrt2nd=wrt2nd)

            zuv += yuAi * Aiv + yvAi * Aiu

            for cmt2 in self._symbol_defs.iter_cmt():
                yAiAj = value.diff(cmt1.A, cmt2.A)
                Aju = CmtSolvedAWrt(cmt=cmt2, wrt=wrt)
                zuv += yAiAj * Aju * Aiv

            zuv += yAi * Aiuv

        for symbol in value.free_symbols:
            if isinstance(symbol, Symbol) and symbol.name in scope:
                zuv += value.diff(wrt, symbol) * XWrt(symbol.name, wrt2nd) + value.diff(
                    symbol
                ) * XWrt(symbol.name, wrt, wrt2nd)

        return zuv

    def _compute_closed_form_value_2nd_mixed_partial_deriv(
        self,
        value: Expr,
        wrt: Eta,
        wrt2nd: Eta,
        scope: Scope,
    ) -> Expr:
        """
        Formula:
            zᵤᵥ = yᵤᵥ
                + yᵤF·Fᵥ
                + yᵥF·Fᵤ
                + yFF·Fᵤ·Fᵥ
                + yF·Fᵤᵥ
                + Σᵢ₌₁ᵐ [
                    yᵤAi·Aiᵥ
                    + yᵥAi·Aiᵤ
                    + yFAi·(Fᵤ·Aiᵥ + Fᵥ·Aiᵤ)
                    + Σⱼ₌₁ᵐ yAjAi·Ajᵤ·Aiᵥ
                    + yAi·Aiᵤᵥ
                ]

        Where:
            • yᵤ, yᵥ, yF, yAi, … etc. denote the partial derivatives of y
                w.r.t. u, v, F, Ai, etc (∂y/∂u, ∂y/∂v, ∂y/∂F, ∂y/∂Ai, etc.)
            • Fᵤ, Fᵥ, Fᵤᵥ denote the partials of F(u,v) (∂F/∂u, ∂F/∂v, ∂²F/∂u∂v)
            • Aiᵤ, Aiᵥ, Aiᵤᵥ denote the partials of A_i(u,v) (∂A_i/∂u, ∂A_i/∂v, ∂²A_i/∂u∂v)
        """
        if not issubclass(self._module_cls, ClosedFormSolutionModule):
            return Number(0)
        n_cmt = get_annotated_meta(self._module_cls).n_cmt
        F = ClosedFormSolutionSolvedF()
        yF = value.diff(F)
        yu = value.diff(wrt)
        yv = value.diff(wrt2nd)
        yuv = yu.diff(wrt2nd)
        yuF = yu.diff(F)
        yvF = yv.diff(F)
        yFF = yF.diff(F)
        Fu = ClosedFormSolutionSolvedFWrt(wrt=wrt)
        Fv = ClosedFormSolutionSolvedFWrt(wrt=wrt2nd)
        Fuv = ClosedFormSolutionSolvedFWrt(wrt=wrt, wrt2nd=wrt2nd)
        zuv = yuv + yuF * Fv + yvF * Fu + yFF * Fu * Fv + yF * Fuv

        for cmt_index in range(n_cmt):
            __sln_Ai = ClosedFormSolutionSolvedA(index=cmt_index)
            yuAi = yu.diff(__sln_Ai)
            Aiv = ClosedFormSolutionSolvedAWrt(index=cmt_index, wrt=wrt2nd)
            yvAi = yv.diff(__sln_Ai)
            Aiu = ClosedFormSolutionSolvedAWrt(index=cmt_index, wrt=wrt)
            yFAi = yF.diff(__sln_Ai)
            yAi = value.diff(__sln_Ai)
            Aiuv = ClosedFormSolutionSolvedAWrt(index=cmt_index, wrt=wrt, wrt2nd=wrt2nd)

            zuv += yuAi * Aiv + yvAi * Aiu + yFAi * (Fu * Aiv + Fv * Aiu)
            for cmt2_index in range(n_cmt):
                yAiAj = yAi.diff(
                    ClosedFormSolutionSolvedA(index=cmt2_index),
                )
                Aju = ClosedFormSolutionSolvedAWrt(index=cmt2_index, wrt=wrt)
                zuv += yAiAj * Aju * Aiv

            zuv += yAi * Aiuv

        for symbol in value.free_symbols:
            if isinstance(symbol, Symbol) and symbol.name in scope:
                zuv += value.diff(wrt, symbol) * XWrt(symbol.name, wrt2nd) + value.diff(
                    symbol
                ) * XWrt(symbol.name, wrt, wrt2nd)

        return zuv

    def _eval(self, token: cst.CSTNode, scope: Scope) -> Any:
        """
        Evaluate a token in the context of the given locals and globals.

        Args:
            token (cst.CSTNode): The CST token to evaluate.
            scope (Scope): The scope in which to evaluate the token.

        Returns:
            Any: The result of the evaluation.
        """
        # remove all whitespaces
        expr = "".join([line.strip() for line in unparse(token).splitlines()]).strip()

        try:
            parsed = parse_expr(
                expr,
                transformations=(auto_symbol,),
                local_dict=self._locals,
            )

        except Exception as e:
            rethrow(
                e,
                token,
                source_code=self._source_code,
            )
        if isinstance(parsed, YValue):
            return parsed

        if isinstance(parsed, Expr):
            for symbol in parsed.free_symbols:
                if self._symbol_defs.has_symbol(symbol):
                    continue

                if issubclass(self._module_cls, ClosedFormSolutionModule):
                    if isinstance(
                        symbol, ClosedFormSolutionSolvedF | ClosedFormSolutionSolvedA
                    ):
                        continue
                elif issubclass(self._module_cls, OdeModule):
                    if isinstance(symbol, CmtDADt | CmtSolvedA | CmtDosingParamSymbol):
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
