from __future__ import annotations

import typing
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from sympy import Add, Symbol

from typings import ValueType

__all__ = ["SymbolBlock", "Block"]

SymbolT = typing.TypeVar("SymbolT", bound=Symbol)


def interpret_add_in_slice(o: SymbolBlock[SymbolT], expr: Add) -> int:
    args = expr.args
    if len(args) != 2:
        raise ValueError("Invalid length of add")

    left, right = args
    if isinstance(left, Symbol):
        idx = int(o._els.index(typing.cast(SymbolT, left)) + right)
    elif isinstance(right, Symbol):
        idx = int(left + o._els.index(typing.cast(SymbolT, right)))
    else:
        raise ValueError("Invalid add components in slice")

    return idx


def interpret_slice(o: SymbolBlock[SymbolT], s: slice) -> tuple[int, int]:
    if s.step:
        raise NotImplementedError(f"{o.__class__.__name__} cannot handle slice step")
    if isinstance(s.start, Symbol) and isinstance(s.stop, Symbol):
        idx1 = o._els.index(typing.cast(SymbolT, s.start))
        idx2 = o._els.index(typing.cast(SymbolT, s.stop))
        return idx1, idx2
    elif isinstance(s.start, Add) and isinstance(s.stop, Symbol):
        idx1 = interpret_add_in_slice(o=o, expr=s.start)
        idx2 = o._els.index(typing.cast(SymbolT, s.stop))
        return idx1, idx2
    elif isinstance(s.start, Symbol) and isinstance(s.stop, Add):
        idx1 = o._els.index(typing.cast(SymbolT, s.start))
        idx2 = interpret_add_in_slice(o=o, expr=s.stop)
        return idx1, idx2
    elif isinstance(s.start, int) and isinstance(s.stop, int):
        return s.start, s.stop
    else:
        raise NotImplementedError(
            f"{o.__class__.__name__} cannot handle slice start={s.start}, stop={s.stop}"
        )


class SymbolBlock(typing.Generic[SymbolT]):
    def __init__(
        self, els: list[SymbolT], values: npt.NDArray[np.float64], fixed: bool
    ) -> None:
        self._els = els
        self._values = values
        self._fixed = fixed

    @property
    def els(self) -> list[SymbolT]:
        return [*self._els]

    @property
    def names(self) -> list[str]:
        return [v.name for v in self._els]

    @property
    def fixed(self) -> bool:
        return self._fixed

    @fixed.setter
    def fixed(self, v: bool) -> None:
        self._fixed = v

    @property
    def values(self) -> npt.NDArray[np.float64]:
        return self._values

    @property
    def shape(self) -> tuple[int, ...]:
        return self._values.shape

    def __setitem__(self, __key: tuple[SymbolT, SymbolT], v: float) -> None:
        e1, e2 = __key

        idx1 = self._els.index(e1)
        idx2 = self._els.index(e2)
        self._values[idx1, idx2] = v

    @typing.overload
    def __getitem__(self, __key: SymbolT | str) -> float: ...

    @typing.overload
    def __getitem__(
        self, __key: tuple[SymbolT, SymbolT] | tuple[str, str]
    ) -> float: ...

    @typing.overload
    def __getitem__(
        self, __key: slice | tuple[slice, slice]
    ) -> npt.NDArray[np.float64]: ...

    def __getitem__(
        self,
        __key: SymbolT
        | str
        | tuple[SymbolT, SymbolT]
        | tuple[str, str]
        | slice
        | tuple[slice, slice],
    ) -> float | npt.NDArray[np.float64]:
        if isinstance(__key, tuple):
            e1, e2 = __key
            if isinstance(e1, Symbol) and isinstance(e2, Symbol):
                idx1 = self._els.index(e1)
                idx2 = self._els.index(e2)
                return self._values[idx1, idx2]
            elif isinstance(e1, str) and isinstance(e2, str):
                names = self.names
                idx1 = names.index(e1)
                idx2 = names.index(e2)
                return self._values[idx1, idx2]
            elif isinstance(e1, slice) and isinstance(e2, slice):
                e1_idx1, e1_idx2 = interpret_slice(o=self, s=e1)
                e2_idx1, e2_idx2 = interpret_slice(o=self, s=e2)
                return self._values[e1_idx1:e1_idx2, e2_idx1:e2_idx2]
            else:
                raise ValueError("Invalid tuple argument")
        elif isinstance(__key, slice):
            idx1, idx2 = interpret_slice(o=self, s=__key)
            return self._values[idx1:idx2]
        elif isinstance(__key, str):
            idx = self.names.index(__key)
            return self._values[idx]
        else:
            idx = self._els.index(__key)
            return self._values[idx]


@dataclass
class Block:
    """Lower triangular block.

    Examples
    --------
    >>> block = Block(
    >>>     tril=[
    >>>         1,
    >>>         0, 1
    >>>     ],
    >>>     dimension=2
    >>> )
    >>> # [
    >>> #   [1, 0],
    >>> #   [0, 1]
    >>> # ]
    """

    tril: list[ValueType] | npt.NDArray[np.float64]  # 下三角矩阵的值 (一维数组)
    dimension: int  # block 的 dimension

    def as_full(self) -> npt.NDArray[np.float64]:
        """Make lower triangular block matrix into a full symmetric matrix"""
        tri_lower_indicies = np.tril_indices(self.dimension)
        tri_lower_len = len(tri_lower_indicies[0])
        if len(self.tril) != tri_lower_len:
            raise ValueError(
                "Given n_dim {0} requires {1} parameters, does not match with given length of parameters {2}".format(
                    self.dimension, tri_lower_len, len(self.tril)
                )
            )
        tmp = np.zeros([self.dimension, self.dimension])
        tmp[tri_lower_indicies] = self.tril
        full_mat = tmp + tmp.T - np.diag(np.diag(tmp))

        return full_mat
