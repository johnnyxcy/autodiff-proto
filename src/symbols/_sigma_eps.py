from __future__ import annotations

import typing
from copy import deepcopy
from uuid import uuid4

import numpy as np
import numpy.typing as npt

from symbols._symvar import Block, SymBlock, SymVar
from typings import ValueType


class Eps(SymVar):
    """
    Eps parameter, which is the intraindividual variability in nonlinear mixed effects model.

    Attributes
    ----------
    label : str
        Parameter name.
    init_value : float
        Initial estimates of parameter.
    fixed : bool
        Whether the parameter is fixed.
    sigma : Sigma
        Sigma matrix contains the eps parameters.
    """

    __slots__ = ("_sigma", "_index")

    def __new__(cls, name: str, **kwargs: typing.Any) -> Eps:
        return typing.cast(Eps, super().__new__(cls, name, **kwargs))

    @property
    def sigma(self) -> Sigma:
        """Sigma: Sigma matrix contains the eps parameters."""
        return self._sigma

    @sigma.setter
    def sigma(self, sigma: Sigma) -> None:
        if not isinstance(sigma, Sigma):
            raise ValueError(f"sigma must be an instance of Sigma, not {type(sigma)}")
        self._sigma = sigma

    def __deepcopy__(self, memo: dict[int, typing.Any] | None = None) -> typing.Self:
        raise ValueError("Never deepcopy Eps. Deepcopy Sigma instead")


class Sigma(SymBlock[Eps]):
    """Intraindividual variability Matrix.

    Attributes
    ----------
    names : list[str]
        A list of eps parameter names.
    """

    def __deepcopy__(self, memo: dict[int, typing.Any] | None = None) -> typing.Self:
        names = deepcopy(self.names)
        values = deepcopy(self.values)
        fixed = self.fixed

        epsilons = [Eps(name=name, nocache=True) for name in names]
        self_ = type(self)(els=epsilons, values=values, fixed=fixed)

        for el in epsilons:
            el.sigma = self_

        return self_


@typing.overload
def sigma(init_sigma: ValueType, fixed: bool = False) -> Eps:
    """Create a single block sigma matrix.

    Parameters
    ----------
    init_sigma : ValueType | None, optional
        Initial estimate of element in sigma matrix. Defaults to `1`.
    fixed : bool, optional
        Whether the element should be fixed.
        Defaults to `False`.

    Returns
    -------
    Eps
        A eps parameter.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.eta_cl = omega(0.02)
    >>>         self.eps_prop = sigma(0.09)
    >>>         self.eps_add = sigma(3, fixed=True)
    """
    ...


@typing.overload
def sigma(init_sigma: Block, fixed: bool = False) -> list[Eps]:
    """Create a sigma matrix from a lower triangular block.

    Parameters
    ----------
    init_sigma : Block
        A lower triangular block contains initial estimates of all elements in sigma matrix.
    fixed : bool, optional
        Whether the entire sigma matrix should be fixed.
        Defaults to `False`.

    Returns
    -------
    list[Eps]
        A list of eps parameters.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.eta_cl = omega(0.02)
    >>>         self.eps_prop, self.eps_add = sigma(Block(tril=[0.09, 0, 3], dimension=2))
    """
    ...


@typing.overload
def sigma(
    init_sigma: list[list[ValueType]] | npt.NDArray[np.float64],
    fixed: bool = False,
) -> list[Eps]:
    """Create a sigma matrix from a symmetric matrix.

    Parameters
    ----------
    init_sigma : list[list[ValueType]] | NDArray[float_]
        A symmetric matrix contains initial estimates of all elements in sigma matrix.
    fixed : bool, optional
        Whether the entire sigma matrix should be fixed.
        Defaults to `False`.

    Returns
    -------
    list[Eps]
        A list of eps parameters.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.eta_cl = omega(0.02)
    >>>         self.eps_prop, self.eps_add = sigma([[0.09, 0], [0, 3]])
    """
    ...


def sigma(
    init_sigma: ValueType | Block | npt.NDArray[np.float64] | list[list[ValueType]],
    fixed: bool = False,
) -> Eps | list[Eps]:
    values: npt.NDArray[np.float64]

    unpack = False
    if isinstance(init_sigma, int | float):
        # 单一值的 Sigma 构建，将 eps 初值放置于 1x1 Sigma 的对角线即可
        values = np.array([[init_sigma]], dtype=float)
        unpack = True
    elif isinstance(init_sigma, Block):
        # 使用下三角构建 Sigma 矩阵
        values = init_sigma.as_full()

    elif isinstance(init_sigma, typing.Iterable):
        # init_sigma 是一个 ListLike 的对象 (List / npt.NDArray[np.float64])
        arr = np.array(init_sigma, dtype=float)
        if len(arr.shape) != 2:
            raise ValueError(
                "Only 2-d Sigma matrix is allowed, not a {0} dimensional array".format(
                    len(arr.shape)
                )
            )

        if arr.shape[0] != arr.shape[1]:
            raise ValueError(
                "Can only construct Sigma with block matrix, not a shape of {0} x {1}".format(
                    arr.shape[0], arr.shape[1]
                )
            )

        values = arr

    else:
        raise TypeError("Invalid type of init_sigma {0}".format(type(init_sigma)))

    n_dim = values.shape[0]

    # 校验是否是对称矩阵
    for i in range(1, n_dim):
        if not np.all(np.diag(values, -i) == np.diag(values, i)):
            raise ValueError(
                "Given Sigma \n {0} \n is not symmetric".format(str(values))
            )

    epsilons: list[Eps] = []
    for i in range(n_dim):
        _name = f"__unnamed_eps_{uuid4().hex}"
        epsilons.append(Eps(name=_name))

    sigma = Sigma(els=epsilons, values=values, fixed=fixed)

    for _e in epsilons:
        _e.sigma = sigma

    return epsilons[0] if unpack and len(epsilons) == 1 else epsilons


def sigma_sd(
    init_sigma_sd: ValueType,
    fixed: bool = False,
) -> Eps:
    """Create a single block sigma matrix with sd value.

    Parameters
    ----------
    init_sigma : ValueType | None, optional
        Initial estimate of element in sigma matrix. Defaults to `1`.
    fixed : bool, optional
        Whether the element should be fixed.
        Defaults to `False`.

    Returns
    -------
    Eps
        A eps parameter.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, None))
    >>>         self.eta_cl = omega(0.02)
    >>>         self.eps_prop = sigma_sd(0.09)
    >>>         self.eps_add = sigma_sd(3, fixed=True)
    """
    return sigma(init_sigma=init_sigma_sd**2, fixed=fixed)
