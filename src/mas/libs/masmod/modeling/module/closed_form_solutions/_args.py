from __future__ import annotations

from mas.libs.masmod.modeling.symbols._args import ParamArg
from mas.libs.masmod.modeling.symbols._closed_form import ClosedFormSolutionSolvedF
from mas.libs.masmod.modeling.typings import Expression

ParamKwargs = dict[ParamArg, Expression | None]


def fallback(v: Expression | None, default: Expression) -> Expression:
    if v is None:
        return default
    return v


def solution_with_params(args: ParamKwargs) -> ClosedFormSolutionSolvedF:
    o = ClosedFormSolutionSolvedF()

    setattr(o, "_solve_args_", args)

    return o


def get_args_of_solution(solved_f: ClosedFormSolutionSolvedF) -> ParamKwargs:
    p = getattr(solved_f, "_solve_args_", None)
    if p is None:
        return {}
    return p
