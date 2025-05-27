# _*_ coding: utf-8 _*_
############################################################
# File: @mas/masmod\modeling\module\closed_form_solutions\ev_one_cmt.py
#
# Author: 许翀轶 <chongyi.xu@drugchina.net>
#
# File Created: 05/08/2025 10:32 am
#
# Last Modified: 05/12/2025 02:52 pm
#
# Modified By: 许翀轶 <chongyi.xu@drugchina.net>
#
# Copyright (c) 2025 Maspectra Dev Team
############################################################
from typing import Literal

from module.closed_form_solutions._args import fallback, solution_with_params
from module.defs.closed_form import ClosedFormSolutionModule, annotate
from symbols._args import IndexedParamArg, ParamArg
from symbols._closed_form import ClosedFormSolutionCmt, ClosedFormSolutionSolvedF
from typings import Expression

EvOneCmtIndexType = Literal[0, 1] | Literal["depot", "central"]


class EvOneCmtLinear:
    class _ClosedFormSolution(ClosedFormSolutionModule):
        """Class to solve the one-compartment linear model."""

        @property
        def cmt_depot(self) -> ClosedFormSolutionCmt:
            """Reference to the depot compartment."""
            return ClosedFormSolutionCmt(0)

        @property
        def cmt_central(self) -> ClosedFormSolutionCmt:
            """Reference to the central compartment."""
            return ClosedFormSolutionCmt(1)

    @annotate(
        n_cmt=2,
        defdose_cmt=1,
        defobs_cmt=2,
        advan=2,
        trans=1,
    )
    class Micro(_ClosedFormSolution):
        """Model with micro pharmacokinetic parameters."""

        def solve(
            self,
            k: Expression,
            ka: Expression,
            alag1: Expression | None = None,
            alag2: Expression | None = None,
            s1: Expression | None = None,
            s2: Expression | None = None,
            f1: Expression | None = None,
            f2: Expression | None = None,
            r1: Expression | None = None,
            r2: Expression | None = None,
            d1: Expression | None = None,
            d2: Expression | None = None,
        ) -> ClosedFormSolutionSolvedF:
            """Predict by micro pharmacokinetic parameters in extravascular one compartment

            Parameters
            ----------
            k : Expression
                Rate constant of elimination.
            ka : Expression
                Rate constant of absorption.
            alag1 : Expression | None, optional
                Absorption lag for depot compartment. Defaults to `None`.
            alag2 : Expression | None, optional
                Absorption lag for central compartment. Defaults to `None`.
            s1 : Expression | None, optional
                Scale for depot compartment. Defaults to `None`.
            s2 : Expression | None, optional
                Scale for central compartment. Defaults to `None`.
            f1 : Expression | None, optional
                Bioavailability for depot compartment. Defaults to `None`.
            f2 : Expression | None, optional
                Bioavailability for central compartment. Defaults to `None`.
            r1 : Expression | None, optional
                Dose rate for depot compartment. Defaults to `None`.
            r2 : Expression | None, optional
                Dose rate for central compartment. Defaults to `None`.
            d1 : Expression | None, optional
                Dose duration for depot compartment. Defaults to `None`.
            d2 : Expression | None, optional
                Dose duration for central compartment. Defaults to `None`.

            Returns
            -------
            ClosedFormSolutionSolvedF
                A closed form solution for the one-compartment model.
            """
            return solution_with_params(
                {
                    ParamArg("K"): k,
                    ParamArg("V"): 1,
                    ParamArg("KA"): ka,
                    IndexedParamArg("ALAG", 0): alag1,
                    IndexedParamArg("ALAG", 1): alag2,
                    IndexedParamArg("S", 0): s1,
                    IndexedParamArg("S", 1): s2,
                    IndexedParamArg("F", 0): f1,
                    IndexedParamArg("F", 1): f2,
                    IndexedParamArg("R", 0): r1,
                    IndexedParamArg("R", 1): r2,
                    IndexedParamArg("D", 0): d1,
                    IndexedParamArg("D", 1): d2,
                },
            )

    Trans1 = Micro

    @annotate(
        n_cmt=2,
        defdose_cmt=1,
        defobs_cmt=2,
        advan=2,
        trans=2,
    )
    class Physio(_ClosedFormSolution):
        """Model with physiological pharmacokinetic parameters."""

        def solve(
            self,
            cl: Expression,
            v: Expression,
            ka: Expression,
            alag1: Expression | None = None,
            alag2: Expression | None = None,
            s1: Expression | None = None,
            s2: Expression | None = None,
            f1: Expression | None = None,
            f2: Expression | None = None,
            r1: Expression | None = None,
            r2: Expression | None = None,
            d1: Expression | None = None,
            d2: Expression | None = None,
        ) -> ClosedFormSolutionSolvedF:
            """Predict by physio pharmacokinetic parameters in extravascular one compartment

            Parameters
            ----------
            cl : Expression
                Clearance.
            v : Expression
                Volume of distribution.
            ka : Expression
                Rate constant of absorption.
            alag1 : Expression | None, optional
                Absorption lag for depot compartment. Defaults to `None`.
            alag2 : Expression | None, optional
                Absorption lag for central compartment. Defaults to `None`.
            s1 : Expression | None, optional
                Scale for depot compartment. Defaults to `None`.
            s2 : Expression | None, optional
                Scale for central compartment. Defaults to `None`.
            f1 : Expression | None, optional
                Bioavailability for depot compartment. Defaults to `None`.
            f2 : Expression | None, optional
                Bioavailability for central compartment. Defaults to `None`.
            r1 : Expression | None, optional
                Dose rate for depot compartment. Defaults to `None`.
            r2 : Expression | None, optional
                Dose rate for central compartment. Defaults to `None`.
            d1 : Expression | None, optional
                Dose duration for depot compartment. Defaults to `None`.
            d2 : Expression | None, optional
                Dose duration for central compartment. Defaults to `None`.

            Returns
            -------
            ClosedFormSolutionSolvedF
                A closed form solution for the one-compartment model.
            """
            return solution_with_params(
                {
                    ParamArg("CL"): cl,
                    ParamArg("V"): v,
                    ParamArg("KA"): ka,
                    IndexedParamArg("ALAG", 0): alag1,
                    IndexedParamArg("ALAG", 1): alag2,
                    IndexedParamArg("S", 0): s1,
                    IndexedParamArg("S", 1): fallback(s2, v),
                    IndexedParamArg("F", 0): f1,
                    IndexedParamArg("F", 1): f2,
                    IndexedParamArg("R", 0): r1,
                    IndexedParamArg("R", 1): r2,
                    IndexedParamArg("D", 0): d1,
                    IndexedParamArg("D", 1): d2,
                },
            )

    Trans2 = Physio


class EvOneCmtMichaelisMenten:
    """Pharmacokinetic module of extravenous one compartment model with Michaelis-Menten elimination."""

    def __post_init__(self) -> None:
        raise NotImplementedError(
            "EvOneCmtMichaelisMenten PK closed form is not supported yet"
        )


Advan2 = EvOneCmtLinear
