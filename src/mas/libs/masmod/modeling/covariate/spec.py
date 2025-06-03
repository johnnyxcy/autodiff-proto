import typing
from dataclasses import dataclass

from mas.libs.masmod.modeling.symbols._column import (
    AnyCategoricalColVar,
    AnyContinuousColVar,
)
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.typings import BoundsType, ValueType

CategoricalCovariateInclusionType = typing.Literal["exclude", "linear"]
ContinuousCovariateInclusionType = typing.Literal[
    "exclude", "linear", "piecewise", "exp", "power"
]
AnyCovariatesInclusionType = (
    CategoricalCovariateInclusionType | ContinuousCovariateInclusionType
)
MultiValueType = typing.Sequence[ValueType]
MultiBoundsType = typing.Sequence[BoundsType]


@dataclass(kw_only=True)
class CategoricalCovariateInclusionSpec:
    state: CategoricalCovariateInclusionType
    init: ValueType | list[ValueType] | None = None
    bounds: BoundsType | list[BoundsType] | None = None
    fixed: bool = False


@dataclass(kw_only=True)
class CategoricalCovariateRelation:
    on: Theta
    covariate: AnyCategoricalColVar


@dataclass(kw_only=True)
class CategoricalCovariateInclusion(
    CategoricalCovariateRelation, CategoricalCovariateInclusionSpec
):
    def __str__(self) -> str:
        s = f"{self.on.name} ~ {self.covariate.name} @ {self.state}"

        if self.fixed:
            s += "[FIXED]"

        return s


@dataclass(kw_only=True)
class ContinuousCovariateInclusionSpec:
    state: ContinuousCovariateInclusionType
    init: ValueType | list[ValueType] | None = None
    bounds: BoundsType | list[BoundsType] | None = None
    fixed: bool = False


@dataclass(kw_only=True)
class ContinuousCovariateRelation:
    on: Theta
    covariate: AnyContinuousColVar


@dataclass(kw_only=True)
class ContinuousCovariateInclusion(
    ContinuousCovariateRelation, ContinuousCovariateInclusionSpec
):
    def __str__(self) -> str:
        s = f"{self.on.name} ~ {self.covariate.name} @ {self.state}"

        if self.fixed:
            s += "[FIXED]"
        return s


AnyCovariatesInclusion = CategoricalCovariateInclusion | ContinuousCovariateInclusion
