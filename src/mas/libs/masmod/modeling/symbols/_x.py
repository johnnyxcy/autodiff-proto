from __future__ import annotations

import libcst as cst
from sympy import Symbol

from mas.libs.masmod.modeling.typings import AsCSTExpression


class X(Symbol):
    """
    A class to represent an arbitrary variable X.

    For example, p = tv * exp(iiv), then p can be represented as X('p').
    """

    @property
    def xname(self) -> str:
        """
        Get the name of the variable.
        """
        return self.name


class XWrt(Symbol, AsCSTExpression):
    """
    A class to represent an arbitrary variable X with respect to a symvar wrt.

    For example, p = tv * exp(iiv) and wrt = iiv, then XWrt(p, iiv) = __mX__[p, iiv] = ∂p/∂iiv.
    """

    __slots__ = ("_xname", "_wrt", "_wrt2nd")

    def __new__(cls, xname: str, wrt: Symbol, wrt2nd: Symbol | None = None) -> XWrt:
        if wrt2nd is not None:
            name = f"∂²{xname}/∂{wrt.name}∂{wrt2nd.name}"
        else:
            name = f"∂{xname}/∂{wrt.name}"
        self_ = super().__new__(cls, name)
        self_._xname = xname
        self_._wrt = wrt
        self_._wrt2nd = wrt2nd
        return self_

    @property
    def xname(self) -> str:
        return self._xname

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self):
        """
        Convert the XWrt object to a CST expression.
        """
        slice = [
            cst.SubscriptElement(
                slice=cst.Index(cst.SimpleString(value='"' + self.xname + '"')),
            ),
        ]
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

        return cst.Subscript(value=cst.Name(XTransRack.name), slice=slice)


class XTransRack:
    """
    Representing a dummy getter for the derivatives of any arbitrary variable X to be used in MTran.
    """

    name = "__X__"

    def __getitem__(
        self, __key: tuple[str, Symbol] | tuple[str, Symbol, Symbol | None]
    ) -> XWrt:
        """
        Get the x_wrt expression for the given variable and wrt.
        """
        if len(__key) == 2:
            x, wrt = __key
            wrt2nd = None
        else:
            x, wrt, wrt2nd = __key

        return XWrt(x, wrt, wrt2nd)
