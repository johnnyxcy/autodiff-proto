from __future__ import annotations

from typing import Literal, overload

import libcst as cst
from sympy import Expr, Symbol

from syntax.transformers.inline.flags import never_inline_transpile
from typings import AsCSTExpression

YTypeLiteral = Literal["prediction", "likelihood", "-2loglikelihood"]


class Y(Symbol, AsCSTExpression):
    """
    A class to represent a return value Y with a specific name.

    It can be used to represent a variable that is a return value of a function.
    """

    def __new__(cls) -> Y:
        self_ = super().__new__(cls, "__Y__")
        return self_

    def as_cst_expression(self):
        """
        Convert the Y object to a CST expression.
        """
        return cst.Subscript(
            value=cst.Name(YTransRack.name),
            slice=[
                cst.SubscriptElement(cst.Slice(lower=None, upper=None, step=None)),
            ],
        )


class YType(Symbol, AsCSTExpression):
    """
    A class to represent a return value Y with a specific name.

    It can be used to represent a variable that is a return value of a function.
    """

    def __new__(cls) -> Y:
        self_ = super().__new__(cls, "__Ytype__")
        return self_

    def as_cst_expression(self):
        """
        Convert the Y object to a CST expression.
        """
        return cst.Subscript(
            value=cst.Name(YTransRack.name),
            slice=[
                cst.SubscriptElement(cst.Index(cst.SimpleString(value='"type"'))),
            ],
        )


class YWrt(Symbol, AsCSTExpression):
    """
    A class to represent a return value Y with respect to a symvar wrt.

    For example, wrt = iiv, then YWrt(iiv) = __Y__[iiv] = ∂y/∂iiv.
    """

    __slots__ = ("_wrt", "_wrt2nd")

    def __new__(cls, wrt: Symbol, wrt2nd: Symbol | None = None) -> YWrt:
        if wrt2nd is not None:
            name = f"∂²y/∂{wrt.name}∂{wrt2nd.name}"
        else:
            name = f"∂y/∂{wrt.name}"
        self_ = super().__new__(cls, name)
        self_._wrt = wrt
        self_._wrt2nd = wrt2nd
        return self_

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self):
        """
        Convert the YWrt object to a CST expression.
        """
        slice = []
        if isinstance(self.wrt, AsCSTExpression):
            expr = self.wrt.as_cst_expression()
        else:
            expr = cst.Name(self.wrt.name)

        slice.append(cst.SubscriptElement(cst.Index(expr)))
        if self.wrt2nd is not None:
            if isinstance(self.wrt2nd, AsCSTExpression):
                expr = self.wrt2nd.as_cst_expression()

            else:
                # self.wrt2nd is a Symbol
                expr = cst.Name(self.wrt2nd.name)
            slice.append(cst.SubscriptElement(cst.Index(expr)))

        return cst.Subscript(value=cst.Name(YTransRack.name), slice=slice)


class YTransRack:
    """
    Representing a dummy getter for the derivatives of the return value Y to be used in MTran.
    """

    name = "__Y__"

    @overload
    def __getitem__(self, __slice: slice[None, None, None]) -> Y: ...
    @overload
    def __getitem__(self, __type: Literal["type"]) -> YType: ...
    @overload
    def __getitem__(self, __wrt: Symbol | tuple[Symbol, Symbol]) -> YWrt: ...

    def __getitem__(
        self,
        __arg0: Symbol
        | tuple[Symbol, Symbol]
        | Literal["type"]
        | slice[None, None, None],
    ) -> Y | YType | YWrt:
        """
        Get the x_wrt expression for the given variable and wrt.
        """
        if isinstance(__arg0, slice):
            return Y()
        elif isinstance(__arg0, str) and __arg0 == "type":
            return YType()
        elif isinstance(__arg0, Symbol):
            return YWrt(__arg0)
        elif isinstance(__arg0, tuple):
            return YWrt(__arg0[0], __arg0[1])
        else:
            raise TypeError("不支持的索引类型: {0}".format(type(__arg0)))


class YValue(Expr):
    """
    A class to represent a return value Y with a specific value.
    It can be used to represent a variable that is a return value of a function.
    """

    __slots__ = ("_expr", "_type")

    def __new__(cls, expr: Expr, type: YTypeLiteral) -> YValue:
        self_ = super().__new__(cls)
        self_._expr = expr
        self_._type = type
        return self_

    @property
    def expr(self) -> Expr:
        return self._expr

    @property
    def type(self) -> YTypeLiteral:
        return self._type

    @property
    def flag(self) -> Literal[0, 1, 2]:
        if self._type == "prediction":
            return 0
        elif self._type == "likelihood":
            return 1
        elif self._type == "-2loglikelihood":
            return 2
        else:
            raise ValueError(f"Unknown YValue type: {self._type}")


@never_inline_transpile
def prediction(expr: Expr) -> Expr:
    """
    Mark the return value as prediction.
    """
    return YValue(expr, "prediction")


@never_inline_transpile
def likelihood(expr: Expr, transform: Literal["-2log", False] = False) -> Expr:
    """
    Mark the return value as likelihood.
    If transform is "-2log", it will be marked as -2log likelihood.
    """
    if transform == "-2log":
        return YValue(expr, "-2loglikelihood")
    else:
        return YValue(expr, "likelihood")
