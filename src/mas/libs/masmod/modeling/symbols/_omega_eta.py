from __future__ import annotations

import typing
from copy import deepcopy
from uuid import uuid4

import libcst as cst
import numpy as np
import numpy.typing as npt
from sympy import Symbol

from mas.libs.masmod.modeling.symbols._block import Block, SymbolBlock
from mas.libs.masmod.modeling.typings import AsCSTExpression, CodeGen, ValueType

__all__ = ["omega", "omega_sd", "omega_iov", "omega_iov_sd", "Omega", "OmegaIOV", "Eta"]


class Eta(Symbol, AsCSTExpression):
    """
    Eta (η) parameter.
    Represents the interindividual variability (IIV) in a nonlinear mixed effects model.

    Attributes
    ----------
    label : str
        Parameter name.
    init_value : float
        Initial estimates of parameter.
    fixed : bool
        Whether the parameter is fixed.
    omega : Omega
        Omega matrix contains the eta parameters.
    """

    __slots__ = "_omega"

    def __new__(cls, name: str, **kwargs: typing.Any) -> Eta:
        instance = typing.cast(Eta, super().__new__(cls, name, **kwargs))
        return instance

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the Eta object to a CST expression.
        """
        return cst.Attribute(
            value=cst.Name(value="self"),
            attr=cst.Name(value=self.name),
        )

    @property
    def omega(self) -> Omega:
        """Omega: Omega matrix contains the eta parameters."""
        return self._omega

    @omega.setter
    def omega(self, omega: Omega) -> None:
        if not isinstance(omega, Omega):
            raise ValueError(f"omega must be an instance of Omega, not {type(omega)}")
        self._omega = omega

    def __deepcopy__(self, memo: dict[int, typing.Any] | None = None) -> typing.Self:
        raise ValueError("Never deepcopy Eta. Deepcopy Omega instead")


class Omega(SymbolBlock[Eta], CodeGen):
    """Interindividual variability matrix.


    Attributes
    ----------
    names : list[str]
        A list of eta parameter names.
    """

    def __deepcopy__(self, memo: dict[int, typing.Any] | None = None) -> typing.Self:
        names = deepcopy(self.names)
        values = deepcopy(self.values)
        fixed = self.fixed

        etas = [Eta(name=name, nocache=True) for name in names]
        self_ = type(self)(els=etas, values=values, fixed=fixed)

        for el in etas:
            el.omega = self_

        return self_

    def _code_gen(self):
        values = self.values

        lhs_targets = [
            cst.AssignTarget(
                cst.Attribute(value=cst.Name("self"), attr=cst.Name(value=name))
            )
            for name in self.names
        ]

        args = []
        if len(self.names) > 1:  # more than one element on lhs
            mat_els: list[cst.Element] = []
            for row in values:
                mat_els.append(
                    cst.Element(
                        cst.List([cst.Element(cst.Float(value=str(v))) for v in row])
                    )
                )
            args.append(cst.Arg(cst.List(mat_els)))
        else:
            args.append(cst.Arg(cst.Float(value=str(values[0][0]))))
        if self.fixed:
            args.append(
                cst.Arg(
                    keyword=cst.Name(value="fixed"),
                    value=cst.Name(value=str(self.fixed)),
                )
            )
        rhs = cst.Call(func=cst.Name(value=omega.__name__), args=args)

        return cst.Assign(
            targets=lhs_targets,
            value=rhs,
        )


class OmegaIOV(Omega):
    def __init__(self, els: list[Eta], reference: Omega) -> None:
        # 不能 super init
        self._els = els
        self._reference = reference
        self._values = reference._values

    @property
    def fixed(self) -> bool:
        return self._reference.fixed

    @fixed.setter
    def fixed(self, v: bool) -> None:
        self._reference.fixed = v

    @property
    def values(self) -> npt.NDArray[np.float64]:
        return self._reference.values

    @property
    def shape(self) -> tuple[int, ...]:
        return self._reference.shape

    def __setitem__(self, __key: tuple[Eta, Eta], v: float) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, __key: Eta | str) -> float: ...

    @typing.overload
    def __getitem__(self, __key: tuple[Eta, Eta] | tuple[str, str]) -> float: ...

    @typing.overload
    def __getitem__(
        self, __key: slice | tuple[slice, slice]
    ) -> npt.NDArray[np.float64]: ...

    def __getitem__(
        self,
        __key: Eta
        | str
        | tuple[Eta, Eta]
        | tuple[str, str]
        | slice
        | tuple[slice, slice],
    ) -> float | npt.NDArray[np.float64]:
        raise NotImplementedError()

    @property
    def reference(self) -> Omega:
        return self._reference


@typing.overload
def omega(init_omega: ValueType, fixed: bool = False) -> Eta:
    """Create a single block omega matrix.

    Parameters
    ----------
    init_omega : ValueType | None, optional
        Initial estimate of element in omega matrix. Defaults to `1`.
    fixed : bool, optional
        Whether the element should be fixed.
        Defaults to `False`.

    Returns
    -------
    Eta
        A eta parameter.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.v = theta(10, bounds=(0, None))
    >>>         self.eta_cl = omega(0.02)
    >>>         self.eta_v = omega(0, fixed=True)
    """
    ...


@typing.overload
def omega(init_omega: Block, fixed: bool = False) -> list[Eta]:
    """Create an omega matrix from a lower triangular block.

    Parameters
    ----------
    init_omega : Block
        A lower triangular block contains initial estimates of all elements in omega matrix.
    fixed : bool, optional
        Whether the entire omega matrix should be fixed.
        Defaults to `False`.

    Returns
    -------
    list[Eta]
        A list of eta parameters.

    Examples
    -------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.v = theta(10, bounds=(0, None))
    >>>         self.eta_cl, self.eta_v = omega(Block(tril=[0.05, 0, 0.08], dimension=2))
    """
    ...


@typing.overload
def omega(
    init_omega: list[list[ValueType]] | npt.NDArray[np.float64],
    fixed: bool = False,
) -> list[Eta]:
    """Create an omega matrix from a symmetric matrix.

    Parameters
    ----------
    init_omega : list[list[ValueType]] | NDArray[float_]
        A symmetric matrix contains initial estimates of all elements in omega matrix.
    fixed : bool, optional
        Whether the entire omega matrix should be fixed.
        Defaults to `False`.

    Returns
    -------
    list[Eta]
        A list of eta parameters.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.v = theta(10, bounds=(0, None))
    >>>         self.eta_cl, self.eta_v = omega([[0.05, 0], [0, 0.08]])
    """
    ...


def omega(
    init_omega: ValueType | Block | npt.NDArray[np.float64] | list[list[ValueType]],
    fixed: bool = False,
) -> Eta | list[Eta]:
    values: npt.NDArray[np.float64]

    unpack = False
    if isinstance(init_omega, int | float):
        # 单一值的 Omega 构建，将 eta 初值放置于 1x1 Omega 的对角线即可
        values = np.array([[init_omega]], dtype=float)
        unpack = True

    elif isinstance(init_omega, Block):
        # 使用下三角构建 Omega 矩阵
        values = init_omega.as_full()

    elif isinstance(init_omega, typing.Iterable):
        # init_omega 是一个 ListLike 的对象 (List / np.ndarray)
        arr = np.array(init_omega, dtype=float)
        if len(arr.shape) != 2:
            raise ValueError(
                "Only 2-d Omega matrix is allowed, not a {0} dimensional array".format(
                    len(arr.shape)
                )
            )

        if arr.shape[0] != arr.shape[1]:
            raise ValueError(
                "Can only construct Omega with block matrix, not a shape of {0} x {1}".format(
                    arr.shape[0], arr.shape[1]
                )
            )

        values = arr

    else:
        raise TypeError("Invalid type of init_omega {0}".format(type(init_omega)))

    n_dim = values.shape[0]

    # 校验是否是对称矩阵
    for i in range(1, n_dim):
        if not np.all(np.diag(values, -i) == np.diag(values, i)):
            raise ValueError(
                "Given Omega \n {0} \n is not symmetric".format(str(values))
            )

    etas: list[Eta] = []
    for i in range(n_dim):
        _name = f"__unnamed_eta_{uuid4().hex}"
        etas.append(Eta(name=_name))

    omega = Omega(els=etas, values=values, fixed=fixed)
    for _e in etas:
        _e.omega = omega

    return etas[0] if unpack and len(etas) == 1 else etas


def omega_sd(
    init_omega_sd: ValueType,
    fixed: bool = False,
) -> Eta:
    """Create a single block omega matrix with sd value.

    Parameters
    ----------
    init_omega_sd : ValueType | None, optional
        Initial estimate of element in omega matrix. Defaults to `1`.
    fixed : bool, optional
        Whether the element should be fixed.
        Defaults to `False`.

    Returns
    -------
    Eta
        A eta parameter.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.v = theta(10, bounds=(0, None))
    >>>         self.eta_cl = omega_sd(0.02)
    >>>         self.eta_v = omega_sd(0, fixed=True)
    """
    return omega(init_omega_sd**2, fixed=fixed)


def omega_iov(
    n_same: int,
    init_omega: ValueType | Block | npt.NDArray[np.float64] | list[list[ValueType]],
    fixed: bool = False,
) -> list[Eta]:
    if n_same <= 1:
        raise ValueError(
            f"`omega_iov` with n_same={n_same} means nothing. Use `omega` instead"
        )

    _etas = omega(init_omega, fixed=fixed)

    if isinstance(_etas, list):
        reference = _etas[0].omega
    else:
        reference = _etas.omega
        _etas = [_etas]

    merged: list[Eta] = [*_etas]
    for _ in range(n_same - 1):
        etas_same_i: list[Eta] = []
        for __ in range(len(_etas)):
            etas_same_i.append(Eta(name=f"__unnamed_eta_{uuid4().hex}"))
        iov = OmegaIOV(els=etas_same_i, reference=reference)
        for _eta_same in etas_same_i:
            _eta_same.omega = iov
        merged.extend(etas_same_i)

    return merged


def omega_iov_sd(
    n_same: int,
    init_omega_sd: ValueType,
    fixed: bool = False,
) -> list[Eta]:
    return omega_iov(n_same=n_same, init_omega=init_omega_sd**2, fixed=fixed)
