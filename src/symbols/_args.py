from __future__ import annotations

import typing

import libcst as cst
from sympy import Symbol

from typings import AsCSTExpression


class ParamArg(AsCSTExpression):
    def __init__(self, param_name: str) -> None:
        self._param_name = param_name

    @property
    def param_name(self) -> str:
        return self._param_name

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        return [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
        ]

    def as_cst_expression(self) -> cst.BaseExpression:
        return cst.Subscript(
            value=cst.Name(ParamsArgRack.name),
            slice=self._as_cst_slices(),
        )


class IndexedParamArg(ParamArg):
    def __init__(self, param_name: str, index: int) -> None:
        super().__init__(param_name)
        self._index = index

    @property
    def index(self) -> int:
        return self._index

    @property
    def indexed_param_name(self) -> str:
        return f"{self._param_name}{self._index}"

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        return [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
            cst.SubscriptElement(cst.Index(cst.Integer(value=str(self.index)))),
        ]


class ParamArgWrt(AsCSTExpression):
    def __init__(
        self,
        param_arg: str,
        wrt: Symbol,
        wrt2nd: Symbol | None = None,
    ) -> None:
        self._param_name = param_arg
        self._wrt = wrt
        self._wrt2nd = wrt2nd

    @property
    def param_name(self) -> str:
        return self._param_name

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        slice_elements: list[cst.SubscriptElement] = [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
        ]
        if isinstance(self.wrt, AsCSTExpression):
            slice_elements.append(
                cst.SubscriptElement(cst.Index(self.wrt.as_cst_expression()))
            )
        else:
            slice_elements.append(
                cst.SubscriptElement(
                    cst.Index(cst.Attribute(cst.Name("self"), cst.Name(self.wrt.name)))
                )
            )
        if self.wrt2nd is not None:
            if isinstance(self.wrt2nd, AsCSTExpression):
                slice_elements.append(
                    cst.SubscriptElement(cst.Index(self.wrt2nd.as_cst_expression()))
                )
            else:
                slice_elements.append(
                    cst.SubscriptElement(
                        cst.Index(
                            cst.Attribute(cst.Name("self"), cst.Name(self.wrt2nd.name))
                        )
                    )
                )
        return slice_elements

    def as_cst_expression(self) -> cst.BaseExpression:
        return cst.Subscript(
            value=cst.Name(ParamsArgRack.name),
            slice=self._as_cst_slices(),
        )


class IndexedParamArgWrt(ParamArgWrt):
    def __init__(
        self,
        param_arg: tuple[str, int],
        wrt: Symbol,
        wrt2nd: Symbol | None = None,
    ) -> None:
        super().__init__(param_arg[0], wrt, wrt2nd)
        self._index = param_arg[1]

    @property
    def index(self) -> int:
        return self._index

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        slices = super()._as_cst_slices()
        return [
            slices[0],
            cst.SubscriptElement(cst.Index(cst.Integer(value=str(self.index)))),
            *slices[1:],
        ]


class ParamsArgRack:
    """
    Representing a dummy getter for ParamArg symbol and the corresponding derivatives to be used in MTran.
    """

    name: str = "__P__"

    def __init__(
        self,
        cls_param_arg: type[ParamArg] = ParamArg,
        cls_indexed_param_arg: type[IndexedParamArg] = IndexedParamArg,
        cls_param_arg_wrt: type[ParamArgWrt] = ParamArgWrt,
        cls_indexed_param_arg_wrt: type[IndexedParamArgWrt] = IndexedParamArgWrt,
    ):
        self._cls_param_arg = cls_param_arg
        self._cls_indexed_param_arg = cls_indexed_param_arg
        self._cls_param_arg_wrt = cls_param_arg_wrt
        self._cls_indexed_param_arg_wrt = cls_indexed_param_arg_wrt

    def __setitem__(self, __key: typing.Any, __value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, __key: str) -> ParamArg:
        """Get a parameter argument by its name."""
        ...

    @typing.overload
    def __getitem__(self, __key: tuple[str, int]) -> IndexedParamArg:
        """Get a indexed parameter argument by its name and index."""
        ...

    @typing.overload
    def __getitem__(
        self,
        __key: tuple[str, Symbol] | tuple[str, Symbol, Symbol],
    ) -> ParamArgWrt:
        """Get a parameter argument derivative with respect to a variable."""
        ...

    @typing.overload
    def __getitem__(
        self, __key: tuple[str, int, Symbol] | tuple[str, int, Symbol, Symbol]
    ) -> IndexedParamArgWrt:
        """Get a indexed parameter argument derivative with respect to a variable."""
        ...

    def __getitem__(
        self,
        __key: str
        | tuple[str, int]
        | tuple[str, Symbol]
        | tuple[str, Symbol, Symbol]
        | tuple[str, int, Symbol]
        | tuple[str, int, Symbol, Symbol],
    ) -> ParamArg | IndexedParamArg | ParamArgWrt | IndexedParamArgWrt:
        if isinstance(__key, str):
            return self._cls_param_arg(param_name=__key)
        elif isinstance(__key, tuple):
            if len(__key) == 2:
                param_name, index_or_wrt = __key

                if isinstance(index_or_wrt, int):
                    return self._cls_indexed_param_arg(
                        param_name=param_name, index=index_or_wrt
                    )
                else:
                    return self._cls_param_arg_wrt(
                        param_arg=param_name, wrt=index_or_wrt
                    )

            elif len(__key) == 3:
                param_name, index_or_wrt, wrt_or_wrt2nd = __key
                if isinstance(index_or_wrt, int):
                    return self._cls_indexed_param_arg_wrt(
                        param_arg=(param_name, index_or_wrt), wrt=wrt_or_wrt2nd
                    )
                else:
                    return self._cls_param_arg_wrt(
                        param_arg=param_name, wrt=index_or_wrt, wrt2nd=wrt_or_wrt2nd
                    )
            elif len(__key) == 4:
                param_name, index, wrt, wrt2nd = __key
                return self._cls_indexed_param_arg_wrt(
                    param_arg=(param_name, index), wrt=wrt, wrt2nd=wrt2nd
                )
            else:
                raise TypeError()
        else:
            raise TypeError()
