from __future__ import annotations

from typing import Literal, overload

import libcst as cst
from sympy import Expr, Symbol

from typings import AsCSTExpression

YTypeLiteral = Literal["prediction", "likelihood", "-2loglikelihood"]


class Y(Symbol, AsCSTExpression):
    """
    A class to represent a return value Y.

    It can be used to represent a variable that is a return value of a function, with a flag indicating its type (prediction/likelihood).
    """

    __slots__ = ("_type",)

    def __new__(cls, type: YTypeLiteral) -> Y:
        self_ = super().__new__(cls, "__Y__")
        self_._type = type
        return self_

    @property
    def type(self) -> YTypeLiteral:
        return self._type

    def as_cst_expression(self):
        """
        Convert the Y object to a CST expression.
        """
        return cst.Subscript(
            value=cst.Name(YTransRack.name),
            slice=[
                cst.SubscriptElement(
                    cst.Index(value=cst.SimpleString(value='"' + self.type + '"'))
                ),
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
    def __getitem__(self, __type: YTypeLiteral) -> Y: ...
    @overload
    def __getitem__(self, __wrt: Symbol, __wrt2nd: Symbol | None = None) -> YWrt: ...

    def __getitem__(
        self,
        __arg0: Symbol | YTypeLiteral,
        __arg1: Symbol | None = None,
    ) -> Y | YWrt:
        """
        Get the x_wrt expression for the given variable and wrt.
        """
        if isinstance(__arg0, str):
            return Y(__arg0)
        else:
            return YWrt(__arg0, __arg1)


def prediction(expr: Expr) -> Y:
    """
    Get the prediction Y object.
    """
    return Y("prediction")


def likelihood(expr: Expr, transform: Literal["-2log", False] = False) -> Y:
    """
    Get the likelihood Y object.
    """
    if transform == "-2log":
        return Y("-2loglikelihood")
    else:
        return Y("likelihood")
