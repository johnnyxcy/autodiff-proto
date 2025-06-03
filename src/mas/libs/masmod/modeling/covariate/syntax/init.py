import math

import libcst as cst
import numpy as np
import polars as pl

from mas.libs.masmod.modeling.covariate.spec import (
    AnyCovariatesInclusion,
    CategoricalCovariateInclusion,
    ContinuousCovariateInclusion,
    ContinuousCovariateInclusionType,
)
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.typings import BoundsType, ValueType

MAX_BOUNDS_VALUE = 1e5


def _get_theta_init_value(
    init: ValueType | None,
    lower: ValueType | None,
    upper: ValueType | None,
    global_init: float,
    status: str,
) -> ValueType:
    if init is None:
        if status == "power":
            init = global_init
        elif status == "exp":
            if (upper is None) or (lower is None):
                init = global_init
            else:
                if global_init > lower and global_init < upper:
                    init = global_init
                else:
                    init = (lower + upper) / 2
                    if init == 0:
                        init = upper / 5
        else:  # linear or piecewise
            if (
                (upper is None)
                or (lower is None)
                or (abs(lower) >= MAX_BOUNDS_VALUE and abs(upper) > MAX_BOUNDS_VALUE)
            ):
                init = global_init * 100
            else:
                if abs(upper) < abs(lower):
                    init = lower * global_init if upper == 0 else upper * global_init
                else:
                    init = upper * global_init if lower == 0 else lower * global_init

    if lower is not None and upper is None:
        if init < lower:
            init = lower * global_init
    elif lower is None and upper is not None:
        if init > upper:
            init = upper * global_init
    elif upper is not None and lower is not None:
        if init > upper or init < lower:
            raise ValueError(f"init {init} with bounds ({lower}, {upper})")
    return init


def _get_continuous_default_bounds(
    _s: ContinuousCovariateInclusionType,
    cov_min: float,
    cov_max: float,
    cov_median: float,
    cov_name: str,
    init: float | list[float] | None = None,
) -> list[BoundsType]:
    if _s == "linear":  # 2
        if cov_median == cov_min:
            upper = MAX_BOUNDS_VALUE
        else:
            upper = 1 / (cov_median - cov_min)

        if cov_median - cov_max == 0:
            lower = -MAX_BOUNDS_VALUE
        else:
            lower = 1 / (cov_median - cov_max)

        use_bounds = [(lower, upper)]
    elif _s == "piecewise":  # 3
        if cov_median == cov_min:
            raise ValueError(
                f"the {cov_name} median and min are equal {cov_min} for covariate {cov_name}, cannot use piecewise parameterization."
            )
        upper = 1 / (cov_median - cov_min)
        upper1 = MAX_BOUNDS_VALUE
        lower = -MAX_BOUNDS_VALUE
        if cov_median == cov_max:
            raise ValueError(
                f"the {cov_name} median and max are equal {cov_max} for covariate {cov_name}, cannot use piecewise parameterization."
            )
        lower1 = 1 / (cov_median - cov_max)
        use_bounds = [(lower, upper), (lower1, upper1)]
    elif _s == "exp":  # 4
        min_diff = cov_min - cov_median
        max_diff = cov_max - cov_median

        if min_diff == 0 or max_diff == 0:
            upper = 0.01
            lower = 100.0
        else:
            low_exp_bound = 0.01
            high_exp_bound = 100.0
            upper = min(
                math.log(low_exp_bound) / min_diff, math.log(high_exp_bound) / max_diff
            )
            lower = max(
                math.log(low_exp_bound) / max_diff, math.log(high_exp_bound) / min_diff
            )
        use_bounds = [(lower, upper)]

    elif _s == "power":  # 5
        use_bounds = [(-100.0, MAX_BOUNDS_VALUE)]
    else:
        raise ValueError(f"state {_s} not supported")

    for i, bounds_ in enumerate(use_bounds):
        lower_, upper_ = bounds_

        if isinstance(init, float | int):
            if lower_ >= init:
                lower_ = -MAX_BOUNDS_VALUE

            if upper_ <= init:
                upper_ = MAX_BOUNDS_VALUE
        use_bounds[i] = (lower_, upper_)

    return [*use_bounds]


def _build_categorical_init_lines(
    param_name: cst.Name,
    inclusion: CategoricalCovariateInclusion,
    data: pl.DataFrame,
    global_init: float,
):
    lines: list[cst.BaseStatement] = []
    lvls = set(data[inclusion.covariate.col_name].unique())
    theta_nums = len(lvls) - 1
    covariate_name = inclusion.covariate.name
    _s = inclusion.state
    inits = inclusion.init
    bounds = inclusion.bounds

    if _s != "exclude":
        if bounds is None:
            if _s == "linear":  # 2
                bounds = [(-1, 5)] * theta_nums
            else:
                raise ValueError(
                    f"can not use state {_s} with categorical {covariate_name}"
                )
        elif (
            isinstance(bounds, tuple)
            and len(bounds) == 2
            and isinstance(bounds[0], ValueType | None)
            and isinstance(bounds[1], ValueType | None)
        ):  # single bounds
            bounds = [bounds] * theta_nums
        elif isinstance(bounds, list):  # multi bounds
            if len(bounds) < theta_nums:
                bounds = bounds + [(-1, 5)] * (theta_nums - len(bounds))
        else:
            raise ValueError(f"{covariate_name} with {_s} bounds type error")

        if isinstance(inits, list):  # multi inits
            if len(inits) >= theta_nums:
                inits = inits[:theta_nums]
            else:
                inits = inits[:] + [None] * (theta_nums - len(inits))
        elif isinstance(inits, ValueType):  # single inits
            inits = [inits] * theta_nums
        else:  # none inits
            inits = [None] * theta_nums

        for idx in range(theta_nums):
            init = inits[idx]
            bound = bounds[idx]
            if not (isinstance(bound, tuple) and len(bound) == 2):
                raise ValueError(f"{covariate_name} with {_s}  bounds {bound} error")
            lower, upper = bound
            init = _get_theta_init_value(
                init=init, lower=lower, upper=upper, global_init=global_init, status=_s
            )

            lines.append(
                cst.SimpleStatementLine(
                    body=[
                        Theta(
                            name=f"{param_name.value}_{idx + 1}",
                            init=init,
                            bounds=(lower, upper),
                            fixed=inclusion.fixed,
                        )._code_gen()
                    ]
                )
            )

    return lines


def _build_continuous_init_lines(
    param_name: cst.Name,
    inclusion: ContinuousCovariateInclusion,
    data: pl.DataFrame,
    global_init: float,
):
    lines: list[cst.BaseStatement] = []

    covariate_name = inclusion.covariate.name
    median = float(np.nanmedian(data[inclusion.covariate.col_name]))
    max = float(np.nanmax(data[inclusion.covariate.col_name]))
    min = float(np.nanmin(data[inclusion.covariate.col_name]))
    _s = inclusion.state
    inits = inclusion.init
    bounds = inclusion.bounds

    if _s != "exclude":
        if bounds is None:
            use_bounds = _get_continuous_default_bounds(
                _s=_s,
                cov_min=min,
                cov_max=max,
                cov_median=median,
                cov_name=covariate_name,
                init=inits,
            )
        elif (
            isinstance(bounds, tuple)
            and len(bounds) == 2
            and isinstance(bounds[0], ValueType | None)
            and isinstance(bounds[1], ValueType | None)
        ):  # single bounds
            use_bounds = [bounds]
        elif isinstance(bounds, list):  # multi bounds
            use_bounds = bounds
        else:
            raise ValueError(f"{covariate_name} with {_s} bounds type error")

        if inits is None or isinstance(inits, ValueType):
            inits = [inits] if _s != "piecewise" else [inits] * 2
        else:
            inits = inits

        if len(use_bounds) >= 1:
            bound = use_bounds[0]
            lower, upper = bound
        else:
            raise ValueError(
                f"{covariate_name} with {_s}  bounds length must be at least 1"
            )

        if len(inits) >= 1:
            init = inits[0]
        else:
            raise ValueError(
                f"{covariate_name} with {_s} inits length must be at least 1"
            )
        init = _get_theta_init_value(
            lower=lower, upper=upper, init=init, global_init=global_init, status=_s
        )

        lines.append(
            cst.SimpleStatementLine(
                body=[
                    Theta(
                        name=f"{param_name.value}_1",
                        init=init,
                        bounds=(lower, upper),
                        fixed=inclusion.fixed,
                    )._code_gen()
                ]
            )
        )

        if _s == "piecewise":
            if len(use_bounds) >= 2:
                bound = use_bounds[1]
                lower, upper = bound
            else:
                raise ValueError(f"{covariate_name} with {_s}  bounds length must be 2")

            if len(inits) >= 2:
                init = inits[1]
            else:
                raise ValueError("inits length error")
            init = _get_theta_init_value(
                lower=lower, upper=upper, init=init, global_init=global_init, status=_s
            )
            lines.append(
                cst.SimpleStatementLine(
                    body=[
                        Theta(
                            name=f"{param_name.value}_2",
                            init=init,
                            bounds=(lower, upper),
                            fixed=inclusion.fixed,
                        )._code_gen()
                    ]
                )
            )

    return lines


def include_covariate_in_init(
    param_name: cst.Name,
    inclusion: AnyCovariatesInclusion,
    data: pl.DataFrame,
    global_init: float = 1.0,
) -> list[cst.BaseStatement]:
    if isinstance(inclusion, CategoricalCovariateInclusion):
        return _build_categorical_init_lines(param_name, inclusion, data, global_init)
    elif isinstance(inclusion, ContinuousCovariateInclusion):
        return _build_continuous_init_lines(param_name, inclusion, data, global_init)
    else:
        raise ValueError(f"Unsupported case type {type(inclusion)}")
