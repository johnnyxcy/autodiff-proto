from __future__ import annotations

import typing

from sympy import Symbol

from typings import Cstifiable


class SharedVar(Symbol):
    """Wrapped Symbol"""

    __slots__ = ("_init_value", "_dtype")

    def __new__(
        cls,
        name: str,
        init_value: typing.Any,
        **kwargs: typing.Any,
    ) -> SharedVar:
        instance = typing.cast(SharedVar, super().__new__(cls, name, **kwargs))
        if isinstance(init_value, str):
            instance._init_value = init_value
            instance._dtype = "str"
        elif isinstance(init_value, float | int):
            instance._init_value = float(init_value)
            instance._dtype = "numeric"
        else:
            raise TypeError(
                "Type '{}' cannot be used in this context", type(init_value)
            )
        return instance

    @property
    def init_value(self) -> float | str:
        return self._init_value

    @property
    def dtype(self) -> typing.Literal["str", "numeric"]:
        return self._dtype

    def __deepcopy__(self, memo: dict[int, typing.Any]) -> SharedVar:
        d = id(self)
        ins = memo.get(d, None)
        if ins is None:
            ins = SharedVar(
                name=self.name,
                init_value=self._init_value,
            )
        ins.name = self.name
        return ins


class SharedVarValue(Symbol):
    __slots__ = "_variable"

    def __new__(cls, variable: SharedVar) -> SharedVarValue:
        instance = typing.cast(SharedVarValue, super().__new__(cls, variable.name))
        instance._variable = variable
        return instance

    @property
    def variable(self) -> SharedVar:
        return self._variable


class SharedVarValueWrt(Symbol):
    __slots__ = ("_variable", "_wrt", "_wrt2nd")

    def __new__(
        cls, variable: SharedVar, wrt: Symbol, wrt2nd: Symbol | None = None
    ) -> SharedVarValueWrt:
        name = f"d{variable.name}_d{wrt.name}"
        if wrt2nd:
            name += f"_d{wrt2nd.name}"
        instance = typing.cast(SharedVarValueWrt, super().__new__(cls, name))
        instance._variable = variable
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def variable(self) -> SharedVar:
        return self._variable

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd


class SharedVarValueRack(Cstifiable):
    """
    Representing a dummy getter for SharedVar symbol and the corresponding derivatives to be used in MTran.
    """

    name = "__COM__"

    def __setitem__(self, __key: typing.Any, __value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, __key: SharedVar) -> SharedVarValue: ...

    @typing.overload
    def __getitem__(self, __key: tuple[SharedVar, Symbol]) -> SharedVarValueWrt: ...

    def __getitem__(
        self, __key: SharedVar | tuple[SharedVar, Symbol]
    ) -> SharedVarValue | SharedVarValueWrt:
        if isinstance(__key, SharedVar):
            return SharedVarValue(__key)
        elif isinstance(__key, tuple):
            v, wrt = __key
            return SharedVarValueWrt(v, wrt=wrt)
        else:
            raise TypeError()
