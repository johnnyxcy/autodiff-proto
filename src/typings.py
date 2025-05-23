from typing import Protocol, runtime_checkable

import libcst as cst
from sympy import Expr

ValueType = int | float
Expression = int | float | Expr
BoundsType = tuple[ValueType | None, ValueType | None]


@runtime_checkable
class Cstifiable(Protocol):
    def as_cst(self) -> cst.CSTNode:
        """
        Object is convertible to a CST expression.
        """
        ...
