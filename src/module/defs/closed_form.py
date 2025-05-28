from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, TypeVar

from module.defs.module import Module
from symbols._closed_form import ClosedFormSolutionSolvedF
from syntax.transformers.inline_func_transpile import never_inline_transpile

__all__ = [
    "ClosedFormSolutionModule",
    "ClosedFormSolutionModuleMeta",
    "get_annotated_meta",
    "annotate",
]


class ClosedFormSolutionModule(Module):
    def __post_init__(self):
        never_inline_transpile(type(self).solve)
        return super().__post_init__()

    @abc.abstractmethod
    def solve(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> ClosedFormSolutionSolvedF:
        """Solve the closed-form solution.

        Note: This method must be implemented in subclasses.
        """
        raise NotImplementedError("The solve method must be implemented in subclasses.")


ClosedFormSolutionModuleClsT = TypeVar(
    "ClosedFormSolutionModuleClsT", bound=type[ClosedFormSolutionModule]
)


@dataclass
class ClosedFormSolutionModuleMeta:
    n_cmt: int = 0
    defdose_cmt: int = 0  # start from 1
    defobs_cmt: int = 0  # start from 1

    advan: int = 0
    trans: int = 0

    def __call__(
        self, cls: ClosedFormSolutionModuleClsT
    ) -> ClosedFormSolutionModuleClsT:
        if not issubclass(cls, ClosedFormSolutionModule):
            raise TypeError(f"Invalid class type: {cls}.")
        if not hasattr(cls, "solve"):
            raise TypeError(f"Class {cls} must have a solve method.")
        setattr(
            cls,
            "_m_cfsln_meta_",
            self,
        )
        return cls


annotate = ClosedFormSolutionModuleMeta


def get_annotated_meta(
    cls: type[ClosedFormSolutionModule],
) -> ClosedFormSolutionModuleMeta:
    if not hasattr(cls, "_m_cfsln_meta_"):
        raise ValueError("Invalid ClosedFormModule.")
    return getattr(
        cls,
        "_m_cfsln_meta_",
    )
