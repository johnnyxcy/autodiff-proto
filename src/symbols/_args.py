from __future__ import annotations

import typing

import libcst as cst

from symbols._symvar import SymVar
from symbols.to_cst import Cstifiable


class ParamArg(Cstifiable):
    def __init__(self, param_name: str) -> None:
        self.__param_name = param_name

    @property
    def param_name(self) -> str:
        return self.__param_name

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        return [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
        ]

    def as_cst(self) -> cst.BaseAssignTargetExpression:
        return cst.Subscript(
            value=cst.Name(ParamsArgRack.name),
            slice=self._as_cst_slices(),
        )


class IndexedParamArg(ParamArg):
    def __init__(self, param_name: str, index: int) -> None:
        super().__init__(param_name)
        self.__index = index

    @property
    def index(self) -> int:
        return self.__index

    @property
    def indexed_param_name(self) -> str:
        return f"{self.__param_name}{self.__index}"

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        return [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
            cst.SubscriptElement(cst.Index(cst.Integer(value=str(self.index)))),
        ]


class ParamArgWrt(Cstifiable):
    def __init__(
        self,
        param_arg: str,
        wrt: SymVar,
        wrt2nd: SymVar | None = None,
    ) -> None:
        self.__param_name = param_arg
        self.__wrt = wrt
        self.__wrt2nd = wrt2nd

    @property
    def param_name(self) -> str:
        return self.__param_name

    @property
    def wrt(self) -> SymVar:
        return self.__wrt

    @property
    def wrt2nd(self) -> SymVar | None:
        return self.__wrt2nd

    def _as_cst_slices(self) -> typing.Sequence[cst.SubscriptElement]:
        slice_elements: list[cst.SubscriptElement] = [
            cst.SubscriptElement(cst.Index(cst.SimpleString(value=self.param_name))),
            cst.SubscriptElement(
                cst.Index(cst.Attribute(cst.Name("self"), cst.Name(self.wrt.name)))
            ),
        ]
        if self.wrt2nd is not None:
            slice_elements.append(
                cst.SubscriptElement(
                    cst.Index(
                        cst.Attribute(cst.Name("self"), cst.Name(self.wrt2nd.name))
                    )
                )
            )
        return slice_elements

    def as_cst(self) -> cst.BaseAssignTargetExpression:
        return cst.Subscript(
            value=cst.Name(ParamsArgRack.name),
            slice=self._as_cst_slices(),
        )


class IndexedParamArgWrt(ParamArgWrt):
    def __init__(
        self,
        param_arg: tuple[str, int],
        wrt: SymVar,
        wrt2nd: SymVar | None = None,
    ) -> None:
        super().__init__(param_arg[0], wrt, wrt2nd)
        self.__index = param_arg[1]

    @property
    def index(self) -> int:
        return self.__index

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
        __key: tuple[str, SymVar] | tuple[str, SymVar, SymVar],
    ) -> ParamArgWrt:
        """Get a parameter argument derivative with respect to a variable."""
        ...

    @typing.overload
    def __getitem__(
        self, __key: tuple[str, int, SymVar] | tuple[str, int, SymVar, SymVar]
    ) -> IndexedParamArgWrt:
        """Get a indexed parameter argument derivative with respect to a variable."""
        ...

    def __getitem__(
        self,
        __key: str
        | tuple[str, int]
        | tuple[str, SymVar]
        | tuple[str, SymVar, SymVar]
        | tuple[str, int, SymVar]
        | tuple[str, int, SymVar, SymVar],
    ) -> ParamArg | IndexedParamArg | ParamArgWrt | IndexedParamArgWrt:
        if isinstance(__key, str):
            return ParamArg(param_name=__key)
        elif isinstance(__key, tuple):
            if len(__key) == 2:
                param_name, index_or_wrt = __key

                if isinstance(index_or_wrt, int):
                    return IndexedParamArg(param_name=param_name, index=index_or_wrt)
                else:
                    return ParamArgWrt(param_arg=param_name, wrt=index_or_wrt)

            elif len(__key) == 3:
                param_name, index_or_wrt, wrt_or_wrt2nd = __key
                if isinstance(index_or_wrt, int):
                    return IndexedParamArgWrt(
                        param_arg=(param_name, index_or_wrt), wrt=wrt_or_wrt2nd
                    )
                else:
                    return ParamArgWrt(
                        param_arg=param_name, wrt=index_or_wrt, wrt2nd=wrt_or_wrt2nd
                    )
            elif len(__key) == 4:
                param_name, index, wrt, wrt2nd = __key
                return IndexedParamArgWrt(
                    param_arg=(param_name, index), wrt=wrt, wrt2nd=wrt2nd
                )
            else:
                raise TypeError()
        else:
            raise TypeError()
