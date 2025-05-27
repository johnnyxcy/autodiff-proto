from __future__ import annotations

from symbols._args import ParamArg
from symbols._closed_form import ClosedFormSolutionSolvedF
from typings import Expression

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
