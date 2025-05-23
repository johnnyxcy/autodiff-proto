from typing import Protocol, runtime_checkable

import libcst as cst
from sympy import Expr

ValueType = int | float
Expression = int | float | Expr
BoundsType = tuple[ValueType | None, ValueType | None]


@runtime_checkable
class AsCSTExpression(Protocol):
    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Object is convertible to a CST Expression.
        """
        ...


@runtime_checkable
class CodeGen(Protocol):
    def _code_gen(self) -> cst.BaseStatement | cst.BaseSmallStatement:
        """
        Object is convertible to a CST Node.
        """
        ...
