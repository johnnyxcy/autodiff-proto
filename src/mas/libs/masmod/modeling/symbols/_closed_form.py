from __future__ import annotations

import typing

import libcst as cst
from sympy import Symbol
from typing_extensions import Self

from mas.libs.masmod.modeling.typings import AsCSTExpression

__all__ = [
    "ClosedFormSolutionSolvedA",
    "ClosedFormSolutionSolvedAWrt",
    "ClosedFormSolutionCmt",
    "ClosedFormSolutionSolvedF",
    "ClosedFormSolutionSolvedFWrt",
    "ClosedFormSolutionTransRack",
    "ClosedFormSolveCall",
]


class ClosedFormSolutionSolvedA(Symbol, AsCSTExpression):
    __slots__ = "_index"

    def __new__(cls, index: int) -> Self:
        name = f"__A{index}__"
        instance = super().__new__(cls, name)
        instance._index = index
        return instance

    @property
    def index(self) -> int:
        return self._index

    def as_cst_expression(self):
        slice = [cst.SubscriptElement(cst.Index(cst.Integer(value=str(self.index))))]
        return cst.Subscript(
            value=cst.Name(ClosedFormSolutionTransRack.name),
            slice=slice,
        )


class ClosedFormSolutionSolvedAWrt(Symbol, AsCSTExpression):
    __slots__ = ("_index", "_wrt", "_wrt2nd")

    def __new__(cls, index: int, wrt: Symbol, wrt2nd: Symbol | None = None) -> Self:
        if wrt2nd is not None:
            name = f"A{index}_wrt_{wrt.name}_{wrt2nd.name}"
        else:
            name = f"A{index}_wrt_{wrt.name}"
        instance = super().__new__(cls, name)
        instance._index = index
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def index(self) -> int:
        return self._index

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self):
        slice = [cst.SubscriptElement(cst.Index(cst.Integer(value=str(self.index))))]
        if isinstance(self.wrt, AsCSTExpression):
            wrt1st = cst.SubscriptElement(
                cst.Index(self.wrt.as_cst_expression()),
            )
        else:
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
            if isinstance(self.wrt2nd, AsCSTExpression):
                wrt2nd = cst.SubscriptElement(
                    cst.Index(self.wrt2nd.as_cst_expression()),
                )
            else:
                wrt2nd = cst.SubscriptElement(
                    cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.wrt2nd.name),
                        )
                    )
                )
            slice.append(wrt2nd)

        return cst.Subscript(
            value=cst.Name(ClosedFormSolutionTransRack.name),
            slice=slice,
        )


class ClosedFormSolutionCmt:
    def __init__(self, index: int):
        self.__index = index

    @property
    def A(self) -> ClosedFormSolutionSolvedA:
        return ClosedFormSolutionSolvedA(index=self.__index)


class ClosedFormSolutionSolvedF(Symbol, AsCSTExpression):
    def __new__(cls) -> Self:
        name = "__F__"
        return super().__new__(cls, name)

    def as_cst_expression(self):
        return cst.Subscript(
            value=cst.Name(ClosedFormSolutionTransRack.name),
            slice=[cst.SubscriptElement(cst.Slice(lower=None, upper=None, step=None))],
        )


class ClosedFormSolutionSolvedFWrt(Symbol, AsCSTExpression):
    __slots__ = ("_wrt", "_wrt2nd")

    def __new__(cls, wrt: Symbol, wrt2nd: Symbol | None = None) -> Self:
        if wrt2nd is not None:
            name = f"F_wrt_{wrt.name}_{wrt2nd.name}"
        else:
            name = f"F_wrt_{wrt.name}"
        instance = super().__new__(cls, name)
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self):
        slice = []
        if isinstance(self.wrt, AsCSTExpression):
            wrt1st = cst.SubscriptElement(
                cst.Index(self.wrt.as_cst_expression()),
            )
        else:
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
            if isinstance(self.wrt2nd, AsCSTExpression):
                wrt2nd = cst.SubscriptElement(
                    cst.Index(self.wrt2nd.as_cst_expression()),
                )
            else:
                wrt2nd = cst.SubscriptElement(
                    cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.wrt2nd.name),
                        )
                    )
                )
            slice.append(wrt2nd)

        return cst.Subscript(
            value=cst.Name(ClosedFormSolutionTransRack.name),
            slice=slice,
        )


class ClosedFormSolutionTransRack:  # Dummy
    name: str = "__SLN"

    def __setitem__(self, __key: typing.Any, __value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(
        self, __key: slice[None, None, None]
    ) -> ClosedFormSolutionSolvedF: ...

    @typing.overload
    def __getitem__(
        self, __key: Symbol | tuple[Symbol, Symbol]
    ) -> ClosedFormSolutionSolvedFWrt: ...

    @typing.overload
    def __getitem__(self, __key: int) -> ClosedFormSolutionSolvedA: ...

    @typing.overload
    def __getitem__(
        self, __key: tuple[int, Symbol] | tuple[int, Symbol, Symbol]
    ) -> ClosedFormSolutionSolvedAWrt: ...

    def __getitem__(
        self,
        __key: slice[None, None, None]
        | Symbol
        | tuple[Symbol, Symbol]
        | int
        | tuple[int, Symbol]
        | tuple[int, Symbol, Symbol],
    ) -> (
        ClosedFormSolutionSolvedF
        | ClosedFormSolutionSolvedFWrt
        | ClosedFormSolutionSolvedA
        | ClosedFormSolutionSolvedAWrt
    ):
        if isinstance(__key, slice):
            if __key.start is not None or __key.stop is not None:
                raise ValueError("Slice must be empty")
            return ClosedFormSolutionSolvedF()
        elif isinstance(__key, Symbol):
            return ClosedFormSolutionSolvedFWrt(wrt=__key)
        elif isinstance(__key, int):
            return ClosedFormSolutionSolvedA(index=__key)
        elif isinstance(__key, tuple):
            if len(__key) == 2:
                index_or_wrt, wrt_or_wrt2nd = __key
                if isinstance(index_or_wrt, int):
                    return ClosedFormSolutionSolvedAWrt(
                        index=index_or_wrt, wrt=wrt_or_wrt2nd
                    )
                else:
                    return ClosedFormSolutionSolvedFWrt(
                        wrt=index_or_wrt, wrt2nd=wrt_or_wrt2nd
                    )
            else:
                index, wrt, wrt2nd = __key
                if isinstance(index, int):
                    return ClosedFormSolutionSolvedAWrt(
                        index=index, wrt=wrt, wrt2nd=wrt2nd
                    )
                else:
                    raise TypeError()
        else:
            raise TypeError()


class ClosedFormSolveCall:
    name = "__solve__"

    def __call__(self) -> Symbol:
        return Symbol(self.name)
