from __future__ import annotations

import enum
from typing import Any, Literal, Sequence, overload

import libcst as cst
from __version__ import __version__
from libcst.metadata import (
    ExpressionContextProvider,
    ParentNodeProvider,
)
from pandas.api.types import is_float_dtype, is_integer_dtype
from sympy import Add, Basic, Mul, Number, Pow, Symbol, exp, parse_expr
from sympy.core.relational import (
    Equality,
    GreaterThan,
    LessThan,
    Relational,
    StrictGreaterThan,
    StrictLessThan,
    Unequality,
)
from sympy.parsing.sympy_parser import auto_symbol

from mas.libs.masmod.modeling.module.descriptor.distillation import (
    RuntimeModuleDescriptor,
)
from mas.libs.masmod.modeling.symbols._args import (
    IndexedParamArg,
    ParamArg,
    ParamArgTransRack,
    ParamArgWrt,
)
from mas.libs.masmod.modeling.symbols._closed_form import (
    ClosedFormSolutionSolvedA,
    ClosedFormSolutionSolvedAWrt,
    ClosedFormSolutionSolvedF,
    ClosedFormSolutionSolvedFWrt,
    ClosedFormSolutionTransRack,
    ClosedFormSolveCall,
)
from mas.libs.masmod.modeling.symbols._cmt import (
    CmtDADt,
    CmtDADtTransRack,
    CmtDADtWrt,
    CmtParamArg,
    CmtParamArgTransRack,
    CmtParamArgWrt,
    CmtSolvedA,
    CmtSolvedATransRack,
    CmtSolvedAWrt,
    Compartment,
)
from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps
from mas.libs.masmod.modeling.symbols._x import X, XTransRack, XWrt
from mas.libs.masmod.modeling.symbols._y import Y, YTransRack, YType, YWrt
from mas.libs.masmod.modeling.syntax.metadata.scope_provider import ScopeProvider
from mas.libs.masmod.modeling.syntax.rethrow import rethrow
from mas.libs.masmod.modeling.syntax.transformers.autodiff import (
    FIRST_ORDER,
    SECOND_ORDER,
)
from mas.libs.masmod.modeling.syntax.unparse import unparse

MSYMTAB_VARNAME = "__msymtab"
LOCALS_VARNAME = "__locals"
PRED_CONTEXT_VARNAME = "__ctx"
CLOSED_FORM_SOLUTION_VARNAME = ClosedFormSolutionTransRack.name


class ValueType(enum.Enum):
    VALUE_TYPE_VOID = "void"
    VALUE_TYPE_VOID_PTR = "void*"

    VALUE_TYPE_DOUBLE = "double"
    VALUE_TYPE_INT = "int"
    VALUE_TYPE_BOOL = "bool"
    VALUE_TYPE_LONG = "long"
    VALUE_TYPE_STRING = "std::string"

    VALUE_TYPE_VEC = "Eigen::VectorXd"
    VALUE_TYPE_VEC_REF = "Eigen::VectorXd&"
    VALUE_TYPE_VEC_CONST_REF = "const Eigen::VectorXd&"
    VALUE_TYPE_MAT = "Eigen::MatrixXd"
    VALUE_TYPE_MAT_REF = "Eigen::MatrixXd&"
    VALUE_TYPE_MAT_CONST_REF = "const Eigen::MatrixXd&"
    VALUE_TYPE_CUBE_REF = "CubeXd&"

    VALUE_TYPE_CUBE_ARRAY_REF = "Cube<double>&"

    VALUE_TYPE_DOUBLE_PTR = "double*"
    VALUE_TYPE_DOUBLE_CONST_PTR = "const double*"

    VALUE_TYPE_CMT_PTR = "Cmt*"

    VALUE_TYPE_LOCALS_PTR = "Locals*"
    VALUE_TYPE_RNG_PTR = "Rng*"
    VALUE_TYPE_PRED_CTX_PTR = "PredContext*"

    # region Internal
    VALUE_TYPE__INTERNAL_SIM_CONTEXT_TARGET = "ICallSim"
    VALUE_TYPE__INTERNAL_CALL_RANDOM_FUNC = "CallRandom"

    # endregion
    def to_cc_type(self) -> str:
        return self.value

    def is_ptr(self) -> bool:
        return self.value in [
            ValueType.VALUE_TYPE_CMT_PTR.value,
            ValueType.VALUE_TYPE_RNG_PTR.value,
            ValueType.VALUE_TYPE_LOCALS_PTR.value,
            ValueType.VALUE_TYPE_PRED_CTX_PTR.value,
        ]

    def is_bool_like(self) -> bool:
        return self.value == ValueType.VALUE_TYPE_BOOL.value or self.is_numeric()

    def is_numeric(self) -> bool:
        return (
            self.value == ValueType.VALUE_TYPE_DOUBLE.value
            or self.value == ValueType.VALUE_TYPE_INT.value
            or self.value == ValueType.VALUE_TYPE_LONG.value
        )

    def can_be_eq_to(self, other: ValueType) -> bool:
        """与 A == B 不同, 这里会判断 Subroutine 和 numeric 的逻辑"""
        if self.is_numeric() and other.is_numeric():
            return True

        return self == other

    @classmethod
    def from_val(cls, val: Any) -> ValueType:
        typ: ValueType | None = None

        if isinstance(val, float):
            typ = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(val, bool):
            typ = ValueType.VALUE_TYPE_INT
        elif isinstance(val, int):
            if val <= -2147483648 or val >= 2147483647:
                typ = ValueType.VALUE_TYPE_LONG
            else:
                typ = ValueType.VALUE_TYPE_INT
        elif isinstance(val, str):
            typ = ValueType.VALUE_TYPE_STRING

        if typ is None:
            raise TypeError("不支持的 const 类型: {0}".format(type(val)))

        return typ

    @classmethod
    def from_dtype(cls, dtype: Any) -> ValueType:
        typ: ValueType | None = None

        if is_integer_dtype(dtype):
            typ = ValueType.VALUE_TYPE_INT
        elif is_float_dtype(dtype):
            typ = ValueType.VALUE_TYPE_DOUBLE
        if typ is None:
            raise TypeError("不支持的 dtype: {0}".format(dtype))
        return typ


def mask_self_attr(name: str) -> str:
    """
    Mangle the attribute name to avoid conflicts with the `self` keyword.
    """
    return "__self_" + name


def unmask_self_attr(name: str) -> str:
    """
    Unmangle the attribute name to get the original name.
    """
    if name.startswith("__self_"):
        return name[7:]
    return name


class ArbitraryVariableNamer:
    """
    A class to generate arbitrary variable names.
    """

    def __init__(self):
        self._counter = 0
        self._cache: dict[str, str] = {}

    @overload
    def get_name(
        self, __x: X | XWrt, create_if_missing: Literal[False]
    ) -> str | None: ...

    @overload
    def get_name(
        self, __x: X | XWrt, create_if_missing: Literal[True] = True
    ) -> str: ...

    def get_name(self, __x: X | XWrt, create_if_missing: bool = True) -> str | None:
        """
        Get the next variable name.
        """
        if __x.name in self._cache:
            return self._cache[__x.name]
        elif not create_if_missing:
            return None
        name = f"__X_{self._counter}"
        self._counter += 1
        self._cache[__x.name] = name
        return name


class CCTransPredVisitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        ScopeProvider,
        ExpressionContextProvider,
    )

    def __init__(
        self,
        source_code: str,
        descriptor: RuntimeModuleDescriptor,
        advan_trans: tuple[str, str] = ("ADVAN_UNKNOWN", "TRANS_UNKNOWN"),
    ):
        self._translated: list[str] = []
        self._source_code = source_code
        self._descriptor = descriptor
        self._advan_type, self._trans_type = advan_trans
        self._namer = ArbitraryVariableNamer()

        self._declarations: dict[str, ValueType] = {}

        self._locals = {
            **self._descriptor.locals,
            XTransRack.name: XTransRack(),
            YTransRack.name: YTransRack(),
            FIRST_ORDER.name: FIRST_ORDER,
            SECOND_ORDER.name: SECOND_ORDER,
        }

        if self._descriptor.is_closed_form_solution:
            self._locals[ParamArgTransRack.name] = ParamArgTransRack()
            self._locals[ClosedFormSolutionTransRack.name] = (
                ClosedFormSolutionTransRack()
            )
            self._locals[ClosedFormSolveCall.name] = ClosedFormSolveCall()

        if self._descriptor.class_type == "OdeModule":
            self._locals[CmtParamArgTransRack.name] = CmtParamArgTransRack()
            self._locals[CmtDADtTransRack.name] = CmtDADtTransRack()
            self._locals[CmtSolvedATransRack.name] = CmtSolvedATransRack()

    def visit_FunctionDef(self, node):
        if node.name.value != "pred":
            rethrow(
                NotImplementedError("Only 'pred' function is supported"),
                node,
                self._source_code,
            )

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        _returns: list[str] = []
        scope = self.get_metadata(ScopeProvider, original_node.body, None)
        if scope is None:
            return
        _returns.extend(
            [
                "__return:",
                "{",
                f"if ({LOCALS_VARNAME} != nullptr)",
                "{",
            ]
        )
        for assignment in scope.assignments:
            name = assignment.name
            if name == "self":
                continue
            if name.startswith("__"):
                continue  # skip private variables
            _returns.append(f'(*{LOCALS_VARNAME}->dlocals)["{name}"] = {name};')

        # 导出共享变量
        for sharedvar in self._descriptor.sharedvars:
            _returns.append(
                f'(*{LOCALS_VARNAME}->dlocals)["{sharedvar.name}"] = {mask_self_attr(sharedvar.name)};'
            )

        _returns.extend(
            [
                "}",
                "return Ok();",
                "}",
            ]
        )

        # declarations
        declarations: list[str] = []
        for name, value_type in self._declarations.items():
            if value_type.is_ptr():
                declarations.append(f"{value_type.to_cc_type()} {name} = nullptr;")
            elif value_type.is_numeric():
                declarations.append(
                    f"{ValueType.VALUE_TYPE_DOUBLE.to_cc_type()} {name} = 0.;"
                )
            elif value_type == ValueType.VALUE_TYPE_STRING:
                declarations.append(
                    f'{ValueType.VALUE_TYPE_STRING.to_cc_type()} {name} = "";'
                )
            else:
                rethrow(
                    NotImplementedError(f"Unsupported value type: {value_type}"),
                    original_node,
                    self._source_code,
                )

        if self._descriptor.is_closed_form_solution:
            declarations.append(
                f"{ClosedFormSolutionTransRack.name} = {PRED_CONTEXT_VARNAME}->pk->solver->ref({PRED_CONTEXT_VARNAME}->pk->solve_ctx);"
            )

        if self._descriptor.class_type == "OdeModule":
            for cmt in self._descriptor.cmts:
                declarations.append(
                    f"{ValueType.VALUE_TYPE_CMT_PTR.to_cc_type()} {mask_self_attr(cmt.name)} = {MSYMTAB_VARNAME}->{mask_self_attr(cmt.name)};"
                )

        self._translated = [
            f"Result<void> __pred({ValueType.VALUE_TYPE_PRED_CTX_PTR.to_cc_type()}* {PRED_CONTEXT_VARNAME})",
            "{",
            "// #region Declarations",
            f"__SymbolTable* {MSYMTAB_VARNAME} = reinterpret_cast<__SymbolTable*>({PRED_CONTEXT_VARNAME}->symtab);",
            f"Locals* {LOCALS_VARNAME} = {PRED_CONTEXT_VARNAME}->locals;",
            *self.__retrieve_theta_from_self(),
            *self.__retrieve_etas_from_self(),
            *self.__retrieve_eps_from_self(),
            *self.__retrieve_colvars_from_self(),
            *declarations,
            "// #endregion",
            "",
            "// #region Body",
            *self._translated,
            "// #endregion",
            "",
            "// #region Return",
            *_returns,
            "// #endregion",
            "}",
        ]

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine):
        translated: list[str] = []
        if len(node.body) != 1:
            rethrow(
                NotImplementedError(
                    "Unsupported SimpleStatementLine with multiple statements"
                ),
                node,
                self._source_code,
            )

        translated.append(f"\n// {unparse(node.body[0]).strip()}")

        self._translated.extend(translated)

    def visit_If(self, node: cst.If):
        """
        Translate the if statement.
        """
        condition = node.test
        if not isinstance(condition, cst.BaseExpression):
            rethrow(
                NotImplementedError("Unsupported if condition type"),
                node,
                self._source_code,
            )

        condition_type, condition_str = self._translate_rhs(condition)

        if not condition_type.is_bool_like():
            rethrow(
                TypeError(f"Condition must be bool-like, got {condition_type}"),
                node,
                self._source_code,
            )

        self._translated.append(f"if ({condition_str}) {{")

    def leave_If(self, original_node: cst.If):
        self._translated.append("}")
        return None

    def visit_Expr(self, node: cst.Expr):
        if isinstance(node.value, cst.Call):
            func_ = self._eval(node.value.func)
            if isinstance(func_, ClosedFormSolveCall):
                self._translated.append(
                    f"(_try_call_({PRED_CONTEXT_VARNAME}->pk->solver->solve({CLOSED_FORM_SOLUTION_VARNAME}, {PRED_CONTEXT_VARNAME}->pk->solve_ctx, Advan::{self._advan_type}, Trans::{self._trans_type}, {PRED_CONTEXT_VARNAME}->phase, {PRED_CONTEXT_VARNAME}->n_eta, {PRED_CONTEXT_VARNAME}->first_order, {PRED_CONTEXT_VARNAME}->second_order)));"
                )

    def visit_Assign(self, node: cst.Assign):
        assign_targets = node.targets
        if len(assign_targets) != 1:
            rethrow(
                NotImplementedError("Unsupported multiple assignment targets"),
                node,
                self._source_code,
            )

        rhs = node.value
        right_type, right = self._translate_rhs(rhs)

        target_expr = assign_targets[0].target
        lhs = self._eval(target_expr)
        left_type: ValueType
        lhs_is_name = False
        if isinstance(lhs, XWrt):
            left = self._namer.get_name(lhs)
            lhs_is_name = True
            left_type = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(lhs, ParamArg | ParamArgWrt):
            if isinstance(lhs, ParamArgWrt):
                arg_index = self._compute_param_arg_index(
                    lhs.param_name, wrt=lhs.wrt, wrt2nd=lhs.wrt2nd
                )
            else:
                arg_index = self._compute_param_arg_index(lhs.param_name)
            if arg_index is None:  # not valid, skip
                return None
            param_name, tuple_indexer = arg_index
            if isinstance(lhs, CmtParamArg | CmtParamArgWrt):
                left = f"{mask_self_attr(lhs.cmt.name)}->{lhs.param_name}({tuple_indexer[0]}, {tuple_indexer[1]})"
            elif isinstance(lhs, IndexedParamArg):
                dosing_ = (
                    f"({PRED_CONTEXT_VARNAME}->pk->solve_ctx->dosing->{param_name})"
                )
                left = f"{dosing_}({lhs.index}, {tuple_indexer[0]}, {tuple_indexer[1]})"
            else:
                index_ = f"{self._advan_type}{self._trans_type}::{self._advan_type}{self._trans_type}_{param_name}"
                G3_ = f"({PRED_CONTEXT_VARNAME}->pk->solve_ctx->G3)"
                left = f"{G3_}.data[loc({G3_}, {index_}, {tuple_indexer[0]}, {tuple_indexer[1]})]"
            left_type = ValueType.VALUE_TYPE_DOUBLE

        elif isinstance(lhs, Y):
            left = f"{PRED_CONTEXT_VARNAME}->Y[0]"
            left_type = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(lhs, YType):
            left = f"{PRED_CONTEXT_VARNAME}->Ytype"
            left_type = ValueType.VALUE_TYPE_INT
        elif isinstance(lhs, YWrt):
            index = self._compute_y_index(lhs.wrt, lhs.wrt2nd)
            if index is None:
                return None
            left = f"{PRED_CONTEXT_VARNAME}->Y[{index}]"
            left_type = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(lhs, CmtDADt):
            index = self._compute_ode_index(cmt=lhs.cmt)
            if index is None:
                return None
            left = f"{PRED_CONTEXT_VARNAME}->ode->dAdt[{index}]"
            left_type = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(lhs, CmtDADtWrt):
            index = self._compute_ode_index(cmt=lhs.cmt, wrt=lhs.wrt, wrt2nd=lhs.wrt2nd)
            if index is None:
                return None
            if isinstance(lhs.wrt, CmtSolvedA):
                left = f"{PRED_CONTEXT_VARNAME}->ode->dA[{index}]"
            else:
                left = f"{PRED_CONTEXT_VARNAME}->ode->dAdt[{index}]"
            left_type = ValueType.VALUE_TYPE_DOUBLE
        elif isinstance(lhs, Symbol):  # raw symbol
            lhs_is_name = True
            left = lhs.name
            left_type = right_type
        else:
            rethrow(
                NotImplementedError(f"Unsupported assignment target type: {type(lhs)}"),
                node,
                self._source_code,
            )

        if not left_type.can_be_eq_to(right_type):
            rethrow(
                TypeError(f"Cannot assign {right_type} to {left_type}"),
                node,
                self._source_code,
            )

        if lhs_is_name:
            if left in self._declarations:
                if not self._declarations[left].can_be_eq_to(right_type):
                    rethrow(
                        TypeError(
                            f"Cannot reassign {left} from {self._declarations[left]} to {right_type}"
                        ),
                        node,
                        self._source_code,
                    )
            self._declarations[left] = right_type

        self._translated.append(f"{left} = {right};")

    def visit_Return(self, node: cst.Return):
        if node.value is not None:
            rethrow(
                ValueError("`return` statement must not have a value"),
                node,
                self._source_code,
            )
        self._translated.append("goto __return;")

    @property
    def translated(self) -> Sequence[str]:
        return self._translated

    def _translate_rhs(self, rhs: cst.BaseExpression) -> tuple[ValueType, str]:
        expr = self._eval(rhs)

        if expr == FIRST_ORDER:
            return ValueType.VALUE_TYPE_BOOL, f"{PRED_CONTEXT_VARNAME}->first_order"
        if expr == SECOND_ORDER:
            return ValueType.VALUE_TYPE_BOOL, f"{PRED_CONTEXT_VARNAME}->second_order"

        if isinstance(expr, int):
            return ValueType.VALUE_TYPE_INT, str(expr)

        if isinstance(expr, float):
            return ValueType.VALUE_TYPE_DOUBLE, str(expr)

        if isinstance(expr, str):
            return ValueType.VALUE_TYPE_STRING, f'"{expr}"'

        if isinstance(expr, bool):
            return ValueType.VALUE_TYPE_BOOL, str(expr).lower()

        if isinstance(expr, Basic):
            return ValueType.VALUE_TYPE_DOUBLE, self._translate_sympy(expr)

        rethrow(
            NotImplementedError("Cannot translate expression"),
            rhs,
            self._source_code,
        )

    def _translate_sympy(self, expr: Basic) -> str:
        """
        Translate a sympy expression to C++ code.
        """
        if isinstance(expr, Number):
            return str(expr)
        # region Comparison
        if isinstance(expr, Relational):
            lhs_ = self._translate_sympy(expr.lhs)
            rhs_ = self._translate_sympy(expr.rhs)

            op = ""
            if isinstance(expr, Equality):
                op = "=="
            if isinstance(expr, Unequality):
                op = "!="
            if isinstance(expr, GreaterThan):
                op = ">"
            if isinstance(expr, LessThan):
                op = "<"
            if isinstance(expr, StrictGreaterThan):
                op = ">="
            if isinstance(expr, StrictLessThan):
                op = "<="
            return f"{lhs_} {op} {rhs_}"

        # endregion
        if isinstance(expr, ClosedFormSolutionSolvedF):
            return f"{CLOSED_FORM_SOLUTION_VARNAME}.F()"
        if isinstance(expr, ClosedFormSolutionSolvedFWrt):
            if isinstance(expr.wrt, Eta):
                eta_index = self._descriptor.etas.index(expr.wrt)
                return f"{CLOSED_FORM_SOLUTION_VARNAME}.F({eta_index})"
        if isinstance(expr, ClosedFormSolutionSolvedA):
            return f"{CLOSED_FORM_SOLUTION_VARNAME}.A({expr.index})"
        if isinstance(expr, ClosedFormSolutionSolvedAWrt):
            if isinstance(expr.wrt, Eta):
                eta_index = self._descriptor.etas.index(expr.wrt)
                return f"{CLOSED_FORM_SOLUTION_VARNAME}.A({expr.index, eta_index})"

        if isinstance(expr, CmtDADtWrt):
            index = self._compute_ode_index(
                cmt=expr.cmt, wrt=expr.wrt, wrt2nd=expr.wrt2nd
            )
            if index is None:
                return "0."
            if isinstance(expr.wrt, CmtSolvedA):
                return f"{PRED_CONTEXT_VARNAME}->ode->dA[{index}]"
            else:
                return f"{PRED_CONTEXT_VARNAME}->ode->dAdt[{index}]"

        if isinstance(expr, CmtSolvedA):
            index = self._compute_ode_index(cmt=expr.cmt)
            if index is None:
                return "0."
            return f"{PRED_CONTEXT_VARNAME}->ode->A[{index}]"

        if isinstance(expr, CmtSolvedAWrt):
            index = self._compute_ode_index(
                cmt=expr.cmt, wrt=expr.wrt, wrt2nd=expr.wrt2nd
            )
            if index is None:
                return "0."
            return f"{PRED_CONTEXT_VARNAME}->ode->A[{index}]"

        if isinstance(expr, XWrt):
            x_name = self._namer.get_name(expr, create_if_missing=False)
            if x_name is None:
                x_name = "0.0"
            return x_name

        if isinstance(expr, Symbol):
            for symbol in [
                *self._descriptor.thetas,
                *self._descriptor.etas,
                *self._descriptor.epsilons,
                *self._descriptor.colvars,
            ]:
                if symbol.name == expr.name:
                    return f"{mask_self_attr(symbol.name)}"
            return expr.name
        if isinstance(expr, Add):
            return " + ".join(self._translate_sympy(arg) for arg in expr.args)
        if isinstance(expr, Mul):
            return " * ".join(self._translate_sympy(arg) for arg in expr.args)
        if isinstance(expr, exp):
            to = self._translate_sympy(expr.exp)
            return f"std::exp({to})"
        if isinstance(expr, Pow):
            base = self._translate_sympy(expr.base)
            to = self._translate_sympy(expr.exp)
            return f"std::pow({base}, {to})"

        raise NotImplementedError(f"Unsupported expression type: {type(expr)}")

    def _compute_y_index(self, wrt: Symbol, wrt2nd: Symbol | None = None) -> int | None:
        n_eta = len(self._descriptor.etas)
        n_eps = len(self._descriptor.epsilons)
        if wrt2nd is not None:
            if isinstance(wrt, Eta) and isinstance(wrt2nd, Eps):
                return (
                    1
                    + n_eta
                    + n_eps
                    + self._descriptor.etas.index(wrt) * n_eps
                    + self._descriptor.epsilons.index(wrt2nd)
                )
            if isinstance(wrt, Eta) and isinstance(wrt2nd, Eta):
                return (
                    1
                    + n_eta
                    + n_eps
                    + n_eta * n_eps
                    + self._compute_eta_2nd_partial_index(wrt, wrt2nd)
                )

            raise IndexError(
                f"wrt {wrt.name}, wrt2nd {wrt2nd.name} is invalid second order partial derivative"
            )

        if isinstance(wrt, Eta):
            return 1 + self._descriptor.etas.index(wrt)
        if isinstance(wrt, Eps):
            return 1 + n_eta + self._descriptor.epsilons.index(wrt)

        return None

    def _compute_param_arg_index(
        self,
        param_name: str,
        wrt: Symbol | None = None,
        wrt2nd: Symbol | None = None,  # noqa: F821
    ) -> tuple[str, tuple[int, int]] | None:
        if wrt is None and wrt2nd is None:
            return param_name, (0, 0)

        if isinstance(wrt, Eta) and isinstance(wrt2nd, Eta):
            return param_name, (
                1 + self._descriptor.etas.index(wrt),
                1 + self._descriptor.etas.index(wrt2nd),
            )

        if isinstance(wrt, Eta) and wrt2nd is None:
            return param_name, (1 + self._descriptor.etas.index(wrt), 0)

        return None

    def _compute_ode_index(
        self,
        cmt: Compartment,
        wrt: Symbol | CmtSolvedA | None = None,
        wrt2nd: Symbol | None = None,
    ) -> int | None:
        n_cmt = len(self._descriptor.cmts)
        n_eta = len(self._descriptor.etas)
        cmt_index = self._descriptor.cmts.index(cmt)
        if wrt is None:
            return cmt_index
        elif wrt2nd is None:  # only wrt is given
            if isinstance(wrt, Eta):
                eta_index = self._descriptor.etas.index(wrt)
                return n_cmt + eta_index * n_cmt + cmt_index
            elif isinstance(wrt, CmtSolvedA):
                cmt2_index = self._descriptor.cmts.index(wrt.cmt)
                return cmt_index * n_cmt + cmt2_index
            else:
                return None
        else:
            # TODO(@xuchongyi): 做二阶 ode 的时候这个索引要和 Indexer 对齐
            if isinstance(wrt, Eta) and isinstance(wrt2nd, Eta):
                comb_index = self._compute_eta_2nd_partial_index(wrt, wrt2nd)
                if comb_index == -1:
                    raise IndexError("wrt pair not found")

                return n_cmt + n_cmt * n_eta + comb_index * n_cmt + cmt_index
            else:
                return None

    def _compute_eta_2nd_partial_index(self, eta_i: Eta, eta_j: Eta) -> int:
        # 下三角的索引
        i = self._descriptor.etas.index(eta_i)
        j = self._descriptor.etas.index(eta_j)
        if i == -1 or j == -1:
            return -1

        if i < j:
            j, i = i, j

        return i * (i + 1) // 2 + j

    def _eval(self, token: cst.BaseExpression) -> Any:
        """
        Evaluate the CST token in the current context.
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

        return parsed

    def __retrieve_theta_from_self(self) -> list[str]:
        retrieved_vars: list[str] = []
        for theta in self._descriptor.thetas:
            retrieved_vars.append(
                f"double {mask_self_attr(theta.name)} = {MSYMTAB_VARNAME}->{mask_self_attr(theta.name)};"
            )

        return retrieved_vars

    def __retrieve_etas_from_self(self) -> list[str]:
        retrieved_vars: list[str] = []
        for eta in self._descriptor.etas:
            retrieved_vars.append(
                f"double {mask_self_attr(eta.name)} = {MSYMTAB_VARNAME}->{mask_self_attr(eta.name)};"
            )

        return retrieved_vars

    def __retrieve_eps_from_self(self) -> list[str]:
        retrieved_vars: list[str] = []
        for eps in self._descriptor.epsilons:
            retrieved_vars.append(
                f"double {mask_self_attr(eps.name)} = {MSYMTAB_VARNAME}->{mask_self_attr(eps.name)};"
            )

        return retrieved_vars

    def __retrieve_colvars_from_self(self) -> list[str]:
        retrieved_vars: list[str] = []
        for colvar in self._descriptor.colvars:
            if colvar.dtype == "numeric":
                dtype = "double"
            elif colvar.dtype == "string":
                dtype = "std::string"
            else:
                raise TypeError(f"Unsupported colvar dtype: {colvar.dtype}")
            retrieved_vars.append(
                f"{dtype} {mask_self_attr(colvar.name)} = {MSYMTAB_VARNAME}->{mask_self_attr(colvar.name)};"
            )

        return retrieved_vars


class CCTranslator:
    def __init__(self, descriptor: RuntimeModuleDescriptor):
        self._descriptor = descriptor

        if descriptor.is_closed_form_solution:
            advan_enum = f"ADVAN{descriptor.advan}"
            trans_enum = f"TRANS{descriptor.trans}"
        else:
            advan_enum = "ADVAN_UNKNOWN"
            trans_enum = "TRANS_UNKNOWN"

        self._advan_trans = advan_enum, trans_enum

    def translate(self) -> list[str]:
        """
        Translate the module descriptor to C++ code.
        """
        if self._descriptor.is_closed_form_solution:
            module_type = "ModuleType::MODULE_TYPE_CLOSED_FORM_SOLUTION"
        elif self._descriptor.class_type == "OdeModule":
            module_type = "ModuleType::MODULE_TYPE_ODE"
        else:
            module_type = "ModuleType::MODULE_TYPE_PRED"

        translated: list[str] = [
            f'#define __MASMOD_VERSION__ "{__version__}"',
            *self.__include_headers(),
            *self.__symbol_table_declaration(),
            "",  # empty line
            "class __Module : public IModule",
            "{",
            "public:",
            "ModuleType module_type() const",
            "{",
            "return {};".format(module_type),
            "}",
            "std::unique_ptr<SymbolTable> create_symbol_table() const",
            "{",
            "return std::make_unique<__SymbolTable>();",
            "}",
            f"Advan advan_type() const {{ return Advan::{self._advan_trans[0]}; }}",
            f"Trans trans_type() const {{ return Trans::{self._advan_trans[1]}; }}",
        ]

        visitor = CCTransPredVisitor(
            source_code=self._descriptor.postprocessed_pred.src,
            descriptor=self._descriptor,
            advan_trans=self._advan_trans,
        )
        cst.MetadataWrapper(
            cst.Module([self._descriptor.postprocessed_pred.cst])
        ).visit(visitor)

        translated.extend(visitor.translated)

        translated.append("};")

        translated.extend(self.__module_factory_function())

        return translated

    def __include_headers(self) -> list[str]:
        """生成 include 头文件"""
        contexts = [
            "#include <iostream>",
            "#include <cmath>",
            "#include <memory>",
            "#include <string>",
            '#include "mas/libs/crobat/arrays/arrays.hpp"',
            '#include "mas/libs/masmod/libc/headers.hpp"',
            '#include "mas/libs/crobat/io/io.hpp"',
            '#include "mas/libs/crobat/math/math.hpp"',
            "",
            "using mas::libs::crobat::arrays::loc;",
            "using mas::libs::crobat::io::Ok;",
            "using mas::libs::crobat::io::Err;",
            "using mas::libs::crobat::io::Result;",
            "using mas::libs::crobat::math::distribution::Rng;",
            "using mas::libs::masmod::libc::mod::IModule;",
            "using mas::libs::masmod::libc::mod::ModuleType;",
            "using mas::libs::masmod::libc::mod::PredVariant;",
            "using mas::libs::masmod::libc::mod::PredContext;",
            "using mas::libs::masmod::libc::mod::SymbolTable;",
            "using mas::libs::masmod::libc::mod::NumericSharedVar;",
            "using mas::libs::masmod::libc::mod::Locals;",
            "using mas::libs::masmod::libc::mod::Cmt;",
            "using mas::libs::masmod::libc::mod::Advan;",
            "using mas::libs::masmod::libc::mod::Trans;",
            "",
        ]

        if self._descriptor.is_closed_form_solution:
            contexts.extend(
                [
                    "using mas::libs::masmod::libc::mod::IClosedFormSolver;",
                    "using mas::libs::masmod::libc::mod::ClosedFormSolution;",
                    f"using mas::libs::masmod::libc::mod::{self._advan_trans[0]}{self._advan_trans[1]};",
                ]
            )
        contexts.append(
            """//DECLARE_bool(PROTECTED);
namespace mas {
double log(double v) {
  //if (FLAGS_PROTECTED) {
    if (v <= 0) {
      return 0;
    } else {
      return std::log(v);
    }
  //}
  return std::log(v);
}

} // namespace mas"""
        )
        return contexts

    def __symbol_table_declaration(self) -> list[str]:
        # 声明需要从 self 中获取的参数
        declarations: dict[
            str,
            tuple[Literal["double", "std::string", "Cmt*", "NumericSharedVar"], str],
        ] = {}
        for theta in self._descriptor.thetas:
            declarations[mask_self_attr(theta.name)] = (
                "double",
                "0.0",
            )
        for eta in self._descriptor.etas:
            declarations[mask_self_attr(eta.name)] = (
                "double",
                "0.0",
            )
        for eps in self._descriptor.epsilons:
            declarations[mask_self_attr(eps.name)] = (
                "double",
                "0.0",
            )

        for sharedvar in self._descriptor.sharedvars:
            if sharedvar.dtype == "numeric":
                declarations[mask_self_attr(sharedvar.name)] = (
                    "NumericSharedVar",
                    f"NumericSharedVar({sharedvar.init_value}, {len(self._descriptor.etas)})",
                )
            else:
                raise NotImplementedError(
                    "Shared variable other than numeric dtype is not supported yet"
                )

        for cmt in self._descriptor.cmts:
            cmt_name = mask_self_attr(cmt.name)
            declarations[cmt_name] = ("Cmt*", "nullptr")

        for col_var in self._descriptor.colvars:
            if col_var.dtype == "numeric":
                declarations[mask_self_attr(col_var.name)] = ("double", "0.0")
            else:
                declarations[mask_self_attr(col_var.name)] = ("std::string", "")

        entity_arg_name = "entity"
        varname_arg_name = "varname"

        varname_enum_class_name = "__SymbolTableVarName"
        static_varname_mp_obj_name = "__symtab_varname_mp"

        def varname_to_enum_name(varname: str) -> str:
            return f"{varname_enum_class_name}_{varname}"

        declaration_lines: list[str] = [
            f"{typ} {name} = {default_value};"
            for name, (typ, default_value) in declarations.items()
        ]
        put_numeric_lines: list[str] = [
            f"switch ({static_varname_mp_obj_name}[{varname_arg_name}]) {{"
        ]
        put_string_lines: list[str] = [
            f"switch ({static_varname_mp_obj_name}[{varname_arg_name}]) {{"
        ]

        dynamic_varnames: list[str] = []
        for col_var in self._descriptor.colvars:
            name = mask_self_attr(col_var.name)
            dynamic_varnames.append(name)
            lines = [
                f"case {varname_to_enum_name(name)}:",
                f"this->{name} = {entity_arg_name};",
                "break;",
            ]
            if col_var.dtype == "numeric":
                put_numeric_lines.extend(lines)
            if col_var.dtype == "str":
                put_string_lines.extend(lines)

        put_theta_lines: list[str] = [f"switch ({varname_arg_name}) {{"]
        for idx, theta in enumerate(self._descriptor.thetas):
            lines = [
                f"case {idx}:",
                f"this->{mask_self_attr(theta.name)} = {entity_arg_name};",
                "break;",
            ]
            put_theta_lines.extend(lines)
        put_theta_lines.extend(["default: break;", "}"])

        put_eta_lines: list[str] = [f"switch ({varname_arg_name}) {{"]
        for idx, eta in enumerate(self._descriptor.etas):
            lines = [
                f"case {idx}:",
                f"this->{mask_self_attr(eta.name)} = {entity_arg_name};",
                "break;",
            ]
            put_eta_lines.extend(lines)
        put_eta_lines.extend(["default: break;", "}"])

        put_eps_lines: list[str] = [f"switch ({varname_arg_name}) {{"]
        for idx, eps in enumerate(self._descriptor.epsilons):
            lines = [
                f"case {idx}:",
                f"this->{mask_self_attr(eps.name)} = {entity_arg_name};",
                "break;",
            ]
            put_eps_lines.extend(lines)
        put_eps_lines.extend(["default: break;", "}"])

        put_cmt_lines: list[str] = [f"switch ({varname_arg_name}) {{"]
        for idx, cmt in enumerate(self._descriptor.cmts):
            lines = [
                f"case {idx}:",
                f"this->{mask_self_attr(cmt.name)} = {entity_arg_name};",
                "break;",
            ]
            put_cmt_lines.extend(lines)
        put_cmt_lines.extend(["default: break;", "}"])

        put_numeric_lines.extend(["default: break;", "}"])
        put_string_lines.extend(["default: break;", "}"])
        return [
            "",
            f"enum {varname_enum_class_name} {{",
            ",".join([varname_to_enum_name(name) for name in dynamic_varnames]),
            "};",
            f"static std::unordered_map<std::string, {varname_enum_class_name}> {static_varname_mp_obj_name} = {{",
            ",".join(
                [
                    f'{{"{name}", {varname_to_enum_name(name)}}}'
                    for name in dynamic_varnames
                ]
            ),
            "};",
            "class __SymbolTable : public SymbolTable",
            "{",
            "public:",
            *declaration_lines,
            f"void put_theta(const unsigned int& {varname_arg_name}, const double& {entity_arg_name}) override",
            "{",
            *put_theta_lines,
            "}",
            f"void put_eta(const unsigned int& {varname_arg_name}, const double& {entity_arg_name}) override",
            "{",
            *put_eta_lines,
            "}",
            f"void put_eps(const unsigned int& {varname_arg_name}, const double& {entity_arg_name}) override",
            "{",
            *put_eps_lines,
            "}",
            f"void put_numeric(const std::string& {varname_arg_name}, const double& {entity_arg_name}) override",
            "{",
            *put_numeric_lines,
            "}",
            f"void put_string(const std::string& {varname_arg_name}, const std::string& {entity_arg_name}) override",
            "{",
            *put_string_lines,
            "}",
            f"void put_cmt(const unsigned int& {varname_arg_name}, Cmt* {entity_arg_name}) override",
            "{",
            *put_cmt_lines,
            "}",
            "",
            "};",
            "",
        ]

    def __module_factory_function(self) -> list[str]:
        """生成 module factory 的函数体"""
        return [
            "",
            "__DYLIB_EXPORT IModule* __dylib_module_factory()",
            "{",
            "return new __Module();",
            "}",
            "",
        ]
