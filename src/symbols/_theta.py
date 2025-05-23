from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

import libcst as cst
import numpy as np
from sympy import Symbol

from typings import BoundsType, CodeGen, ValueType

__all__ = ["theta", "Theta"]


class Theta(Symbol, CodeGen):
    """
    Theta parameter, which is the fixed effect in nonlinear mixed effects model.

    Attributes
    ----------
    label : str
        Parameter name.
    init_value : float
        Initial estimates of parameter.
    fixed : bool
        Whether the parameter is fixed.
    bounds : tuple[float | None, float | None]
        Boundary of the theta parameter.
    """

    __slots__ = ("_init_value", "_fixed", "_bounds")

    def __new__(
        cls,
        name: str,
        init_value: ValueType = 0.0,
        bounds: BoundsType | None = None,
        fixed: bool = False,
        **kwargs: Any,
    ) -> Theta:
        instance = cast(Theta, super().__new__(cls, name, **kwargs))
        instance.bounds = bounds
        instance.init_value = init_value
        instance._fixed = fixed
        return instance

    def _code_gen(self):
        args = [
            cst.Arg(value=cst.Float(value=str(self.init_value))),
        ]
        if self.bounds[0] or self.bounds[1]:
            if self.bounds[0] is None:
                lower_ = cst.Name(value="None")
            else:
                lower_ = cst.Float(value=str(self.bounds[0]))

            if self.bounds[1] is None:
                upper_ = cst.Name(value="None")
            else:
                upper_ = cst.Float(value=str(self.bounds[1]))

            args.append(
                cst.Arg(
                    keyword=cst.Name(value="bounds"),
                    value=cst.Tuple(
                        [
                            cst.Element(lower_),
                            cst.Element(upper_),
                        ]
                    ),
                )
            )
        if self.fixed:
            args.append(
                cst.Arg(
                    keyword=cst.Name(value="fixed"),
                    value=cst.Name(value=str(self.fixed)),
                )
            )
        return cst.Assign(
            targets=[cst.AssignTarget(cst.Name(value=self.name))],
            value=cst.Call(
                func=cst.Name(value=theta.__name__),
                args=args,
            ),
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> Theta:
        d = id(self)
        ins = memo.get(d, None)
        if ins is None:
            ins = Theta(
                name=self.name,
                init_value=self._init_value,
                bounds=self._bounds,
                fixed=self.fixed,
            )
        ins.name = self.name
        return ins

    @property
    def init_value(self) -> float:
        """float: Initial value for variable"""
        return self._init_value

    @init_value.setter
    def init_value(self, init_value: ValueType) -> None:
        self._init_value = float(init_value)

    @property
    def fixed(self) -> bool:
        """bool: If variable should be fixed"""
        return bool(self._fixed)

    @property
    def bounds(self) -> tuple[float | None, float | None]:
        """tuple[float | None, float | None]: Boundary of the theta parameter."""
        return self._bounds

    @bounds.setter
    def bounds(self, bounds: BoundsType | None) -> None:
        if bounds is not None:
            if len(bounds) != 2:
                raise ValueError("Invalid length of bounds, expect 2")

            _lower, _upper = bounds

            if _lower is not None and type(_lower) not in [
                float,
                int,
                np.float64,
                np.int64,
            ]:
                raise TypeError(
                    "Invalid argument bound, expect float or int or None, but {0} is given".format(
                        type(_lower)
                    )
                )
            elif _lower is None:
                _lower = None
            else:
                _lower = float(_lower)

            if _upper is not None and type(_upper) not in [
                float,
                int,
                np.float64,
                np.int64,
            ]:
                raise TypeError(
                    "Invalid argument bound, expect float or int or None, but {0} is given".format(
                        type(_lower)
                    )
                )
            elif _upper is None:
                _upper = None
            else:
                _upper = float(_upper)

            bounds = (_lower, _upper)

        else:
            bounds = (None, None)

        self._bounds = bounds


def theta(
    init_value: ValueType, bounds: BoundsType | None = None, fixed: bool = False
) -> Theta:
    """Create a theta parameter.

    Parameters
    ----------
    init_value : ValueType
        Initial estimate of the theta parameter. Defaults to `0`.
    bounds : BoundsType | None, optional
        Lower and upper bounds of the theta parameter estimate for the minimization search.
        If `None`, parameters will not be constrained by bounds. Defaults to `None`.
    fixed : bool, optional
        Whether the theta parameter should be fixed.
        Defaults to `False`.

    Returns
    -------
    Theta
        A theta parameter.

    Examples
    --------
    >>> Class TestModel(Module)
    >>>     def __init__(self):
    >>>         self.cl = theta(0.5, bounds=(0, 10))
    >>>         self.v = theta(10, bounds=(0, None))
    >>>         self.emax = theta(-20, bounds=(-100, 100))
    >>>         self.ec50 = theta(5, fixed=True)
    """

    name = f"__unnamed_theta_{uuid4().hex}"

    return Theta(name=name, init_value=init_value, bounds=bounds, fixed=fixed)
