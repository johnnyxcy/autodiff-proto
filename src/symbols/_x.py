from __future__ import annotations

import libcst as cst
from sympy import Expr, Symbol

from symbols._symvar import SymVar
from symbols.to_cst import Cstifiable


class XWrt(Symbol, Cstifiable):
    """
    A class to represent an arbitrary variable X with respect to a symvar wrt.

    For example, p = tv * exp(iiv) and wrt = iiv, then XWrt(p, iiv) = __mX__[p, iiv] = ∂p/∂iiv.
    """

    __slots__ = ("_wrt", "_wrt2nd")

    def __new__(cls, name: str, wrt: SymVar, wrt2nd: SymVar | None = None) -> XWrt:
        self_ = super().__new__(cls, name)
        self_._wrt = wrt
        self_._wrt2nd = wrt2nd
        return self_

    @property
    def wrt(self) -> SymVar:
        return self._wrt

    @property
    def wrt2nd(self) -> SymVar | None:
        return self._wrt2nd

    def as_cst(self) -> cst.BaseAssignTargetExpression:
        """
        Convert the XWrt object to a CST expression.
        """
        slice = [
            cst.SubscriptElement(
                slice=cst.Index(cst.Name(value=self.name)),
            ),
        ]
        wrt1st = cst.SubscriptElement(
            cst.Index(
                cst.Attribute(
                    value=cst.Name("self"),
                    attr=cst.Name(self.wrt.name),
                )
            )
        )
        slice.append(wrt1st)

        if self.wrt2nd is not None:
            wrt2nd = cst.SubscriptElement(
                cst.Index(
                    cst.Attribute(
                        value=cst.Name("self"),
                        attr=cst.Name(self.wrt2nd.name),
                    )
                )
            )
            slice.append(wrt2nd)

        return cst.Subscript(value=cst.Name(XWrtRack.name), slice=slice)


class XWrtRack:
    """
    Representing a dummy getter for the derivatives of any arbitrary variable X to be used in MTran.
    """

    name = "__X__"

    def __getitem__(self, x: Expr, wrt: SymVar, wrt2nd: SymVar | None = None) -> XWrt:
        """
        Get the x_wrt expression for the given variable and wrt.
        """
        if isinstance(x, Symbol):
            return XWrt(x.name, wrt, wrt2nd)
        raise NotImplementedError(f"Unknown expression type: {type(x)}")
