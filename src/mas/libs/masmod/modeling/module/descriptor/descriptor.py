from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Any, Literal, Sequence, overload

import libcst as cst
import numpy as np
import numpy.typing as npt
import polars as pl
from typing_extensions import Self

from mas.libs.masmod.modeling.module.defs.ode import odeint
from mas.libs.masmod.modeling.module.descriptor.common import (
    ModuleClassTypeLiteral,
    SrcEncapsulation,
)
from mas.libs.masmod.modeling.symbols._cmt import Compartment
from mas.libs.masmod.modeling.symbols._column import (
    AnyCategoricalColVar,
    AnyColVar,
    ColVar,
)
from mas.libs.masmod.modeling.symbols._omega_eta import Eta, Omega
from mas.libs.masmod.modeling.symbols._sharedvar import SharedVar
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps, Sigma
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.syntax.with_comment import with_comment
from mas.libs.masmod.modeling.typings import BoundsType, CodeGen, ValueType
from mas.libs.masmod.modeling.utils.block_diagonal import block_diagonal


@dataclass(kw_only=True, frozen=True)
class ModuleDescriptor(CodeGen):
    # metadata from class
    class_name: str
    class_type: ModuleClassTypeLiteral
    docstring: str | None = None
    configuration: dict[str, Any] = field(default_factory=dict)

    # metadata from __init__
    thetas: list[Theta]
    etas: list[Eta]
    epsilons: list[Eps]
    colvars: list[ColVar]
    cmts: list[Compartment]
    sharedvars: list[SharedVar]
    n_cmt: int
    advan: int
    trans: int
    defdose_cmt: int
    defobs_cmt: int

    # pred src
    preprocessed_pred: SrcEncapsulation[cst.FunctionDef]
    postprocessed_pred: SrcEncapsulation[cst.FunctionDef]

    @property
    def is_closed_form_solution(self) -> bool:
        """bool: If the module is a closed form solution."""
        return self.class_type not in ["OdeModule", "Module"]

    def copy(self):
        self_ = deepcopy(self)

        etas_: list[Eta] = []
        for omega_ in self_.omegas:
            omega_self = deepcopy(omega_)
            etas_.extend(omega_self.els)

        epsilons_: list[Eps] = []
        for sigma_ in self_.sigmas:
            sigma_self = deepcopy(sigma_)
            epsilons_.extend(sigma_self.els)

        self_ = replace(self_, etas=etas_, epsilons=epsilons_)
        return self_

    def _code_gen(self) -> cst.ClassDef:
        """
        Generate the code for the module descriptor.
        """
        class_def_body: list[cst.BaseStatement] = []
        if self.docstring:
            class_def_body.append(
                cst.SimpleStatementLine(
                    body=[cst.Expr(value=cst.SimpleString(value=self.docstring))]
                )
            )
        __init__body: list[cst.BaseStatement] = []
        # super().__init__()
        super_init_args: list[cst.Arg] = []
        if self.class_type == "OdeModule":
            solver = self.configuration.get("odeint.solver", None)
            if solver is not None:
                solver_args: list[cst.Arg] = []
                if solver == "dverk":
                    default_settings = odeint.DVERK().as_configuration_dict()
                elif solver == "lsoda":
                    default_settings = odeint.LSODA().as_configuration_dict()
                else:
                    default_settings = {}

                for key in default_settings:
                    value = self.configuration.get(key, None)
                    if value != default_settings[key]:
                        keyword = key.split(".")[-1]
                        if isinstance(value, bool):
                            if value is True:
                                arg_value = cst.Name(value="True")
                            else:
                                arg_value = cst.Name(value="False")
                        elif isinstance(value, float):
                            arg_value = cst.Float(value=str(value))
                        elif isinstance(value, int):
                            arg_value = cst.Integer(value=str(value))
                        elif isinstance(value, str):
                            arg_value = cst.SimpleString(value=f'"{value}"')
                        else:
                            raise TypeError(
                                f"Unsupported type for solver argument '{key}': {type(value)}"
                            )
                        solver_args.append(
                            cst.Arg(
                                keyword=cst.Name(value=keyword),
                                value=arg_value,
                            )
                        )
                super_init_args.append(
                    cst.Arg(
                        keyword=cst.Name(value="solver"),
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Name(value="odeint"),
                                attr=cst.Name(value=solver.upper()),
                            ),
                            args=solver_args,
                        ),
                    )
                )
        __init__body.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Expr(
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Call(
                                    func=cst.Name(value="super"),
                                    args=[],
                                ),
                                attr=cst.Name(value="__init__"),
                            ),
                            args=super_init_args,
                        )
                    )
                ]
            )
        )
        # theta(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define typical value thetas",
        )
        for i, theta in enumerate(self.thetas):
            line = cst.SimpleStatementLine(body=[theta._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # omega(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define inter-individual variance (iiv) etas",
        )
        visited_omega: set[Omega] = set()
        for i, eta in enumerate(self.etas):
            if eta.omega not in visited_omega:
                line = cst.SimpleStatementLine(body=[eta.omega._code_gen()])
                if i == 0:
                    line = line.with_changes(
                        leading_lines=[cst.EmptyLine(), leading_comment]
                    )
                __init__body.append(line)
                visited_omega.add(eta.omega)

        # sigma(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define random variance (rv) epsilons",
        )
        visited_sigma: set[Sigma] = set()
        for i, eps in enumerate(self.epsilons):
            if eps.sigma not in visited_sigma:
                line = cst.SimpleStatementLine(body=[eps.sigma._code_gen()])
                if i == 0:
                    line = line.with_changes(
                        leading_lines=[cst.EmptyLine(), leading_comment]
                    )
                __init__body.append(line)
                visited_sigma.add(eps.sigma)

        # column(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define covariates (data columns)",
        )
        for i, colvar in enumerate(self.colvars):
            line = cst.SimpleStatementLine(body=[colvar._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # compartment(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define compartments",
        )
        for i, cmt in enumerate(self.cmts):
            line = cst.SimpleStatementLine(body=[cmt._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # sharedvar(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define arbitrary variables",
        )
        for i, sharedvar in enumerate(self.sharedvars):
            line = cst.SimpleStatementLine(body=[sharedvar._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # Compose
        class_def_body.append(
            cst.FunctionDef(
                name=cst.Name(value="__init__"),
                params=cst.Parameters(
                    params=[
                        cst.Param(name=cst.Name(value="self")),
                    ]
                ),
                body=cst.IndentedBlock(body=__init__body),
            )
        )

        class_def_body.append(self.preprocessed_pred.cst)

        return cst.ClassDef(
            name=cst.Name(value=self.class_name),
            bases=[cst.Arg(cst.parse_expression(self.class_type))],
            body=cst.IndentedBlock(body=class_def_body),
        )

    @overload
    def theta_inits(self) -> npt.NDArray[np.float64]: ...

    @overload
    def theta_inits(self, named: Literal[True]) -> dict[str, float]: ...

    def theta_inits(
        self, named: bool = False
    ) -> npt.NDArray[np.float64] | dict[str, float]:
        if not named:
            return np.array([theta.init_value for theta in self.thetas], dtype=float)
        return {
            name: value
            for name, value in [(theta.name, theta.init_value) for theta in self.thetas]
        }

    def theta_names(self) -> list[str]:
        return [theta.name for theta in self.thetas]

    def theta_fixed(self) -> list[bool]:
        return [theta.fixed for theta in self.thetas]

    def theta_bounds(self) -> list[BoundsType]:
        return [theta.bounds for theta in self.thetas]

    def with_theta(
        self,
        theta_inits: (
            Sequence[ValueType]
            | npt.NDArray[np.float64]
            | dict[str, ValueType]
            | ValueType
            | None
        ) = None,
        theta_bounds: dict[str, BoundsType] | BoundsType | None = None,
        theta_fixed: dict[str, bool] | bool | None = None,
    ) -> Self:
        self_ = self.copy()
        # Update thetas
        for i, theta in enumerate(self_.thetas):
            match theta_inits:
                case None:
                    pass
                case dict():
                    if theta.name in theta_inits:
                        theta.init_value = theta_inits[theta.name]
                case float() | int():
                    theta.init_value = theta_inits
                case list() | tuple() | np.ndarray():
                    theta.init_value = theta_inits[i]
                case _:
                    raise TypeError(
                        f"`theta_inits` should be a dict, float, or None. {type(theta_inits)} is not supported."
                    )
            match theta_bounds:
                case None:
                    pass
                case dict():
                    if theta.name in theta_bounds:
                        theta.bounds = theta_bounds[theta.name]
                case tuple():
                    theta.bounds = theta_bounds
                case _:
                    raise TypeError(
                        f"`theta_bounds` should be a dict, tuple, or None. {type(theta_bounds)} is not supported."
                    )
            match theta_fixed:
                case None:
                    pass
                case dict():
                    if theta.name in theta_fixed.keys():
                        theta._fixed = theta_fixed[theta.name]
                case bool():
                    theta._fixed = theta_fixed
                case _:
                    raise TypeError(
                        f"`theta_fixed` should be a list, bool, or None. {type(theta_fixed)} is not supported."
                    )
        return self_

    def eta_inits(self) -> npt.NDArray[np.float64]:
        visited_ids: set[int] = set()
        init_values: npt.NDArray[np.float64] = np.empty([0, 0], dtype=np.float64)

        for _eta in self.etas:
            if id(_eta.omega) not in visited_ids:
                visited_ids.add(id(_eta.omega))
                init_values = block_diagonal(
                    left=init_values,
                    right=_eta.omega.values,
                    fill=np.nan,
                    dtype=np.float64,
                )

        return init_values

    def eta_names(self) -> list[str]:
        return [eta.name for eta in self.etas]

    @property
    def omegas(self) -> list[Omega]:
        omegas: list[Omega] = []
        visited_ids: set[int] = set()
        for _eta in self.etas:
            if id(_eta.omega) not in visited_ids:
                visited_ids.add(id(_eta.omega))
                omegas.append(_eta.omega)
        return omegas

    def with_omega(
        self,
        omega_inits: dict[str, ValueType] | ValueType | None = None,  # diagonal only
        omega_fixed: dict[str, bool] | bool | None | None = None,
    ) -> Self:
        self_ = self.copy()
        omegas_ = self_.omegas
        for omega_ in omegas_:
            etas_in_omega_ = omega_.els
            is_omega_fixed: bool | None = None
            for eta_i in etas_in_omega_:
                if omega_inits is not None:
                    if isinstance(omega_inits, dict):
                        init_value = omega_inits.get(eta_i.name, None)
                    else:
                        init_value = omega_inits
                    if init_value is not None:
                        eta_i.omega[eta_i, eta_i] = init_value
                if isinstance(omega_fixed, dict):
                    this_omega_fixed = omega_fixed.get(eta_i.name, None)
                    if this_omega_fixed is not None:
                        if is_omega_fixed is None:
                            is_omega_fixed = this_omega_fixed
                        else:
                            if is_omega_fixed != this_omega_fixed:
                                raise ValueError("Etas must be fixed within same omega")

            if is_omega_fixed is not None:
                omega_.fixed = is_omega_fixed
            elif isinstance(omega_fixed, bool):
                omega_.fixed = omega_fixed

        return self_

    def eps_inits(self) -> npt.NDArray[np.float64]:
        visited_ids: set[int] = set()
        init_values: npt.NDArray[np.float64] = np.empty([0, 0], dtype=np.float64)

        for _eta in self.epsilons:
            if id(_eta.sigma) not in visited_ids:
                visited_ids.add(id(_eta.sigma))
                init_values = block_diagonal(
                    left=init_values,
                    right=_eta.sigma.values,
                    fill=np.nan,
                    dtype=np.float64,
                )

        return init_values

    def eps_names(self) -> list[str]:
        return [eps.name for eps in self.epsilons]

    @property
    def sigmas(self) -> list[Sigma]:
        sigmas: list[Sigma] = []
        visited_ids: set[int] = set()
        for _eps in self.epsilons:
            if id(_eps.sigma) not in visited_ids:
                visited_ids.add(id(_eps.sigma))
                sigmas.append(_eps.sigma)
        return sigmas

    def with_sigma(
        self,
        sigma_inits: dict[str, ValueType] | ValueType | None = None,  # diagonal only
        sigma_fixed: dict[str, bool] | bool | None | None = None,
    ) -> Self:
        self_ = self.copy()
        sigmas_ = self_.sigmas
        for sigma_ in sigmas_:
            epsilons_in_sigma_ = sigma_.els
            is_sigma_fixed: bool | None = None
            for epsilon_i in epsilons_in_sigma_:
                if sigma_inits is not None:
                    if isinstance(sigma_inits, dict):
                        init_value = sigma_inits.get(epsilon_i.name, None)
                    else:
                        init_value = sigma_inits
                    if init_value is not None:
                        epsilon_i.sigma[epsilon_i, epsilon_i] = init_value
                if isinstance(sigma_fixed, dict):
                    this_sigma_fixed = sigma_fixed.get(epsilon_i.name, None)
                    if this_sigma_fixed is not None:
                        if is_sigma_fixed is None:
                            is_sigma_fixed = this_sigma_fixed
                        else:
                            if is_sigma_fixed != this_sigma_fixed:
                                raise ValueError(
                                    "Epsilons must be fixed within same sigma"
                                )
            if is_sigma_fixed is not None:
                sigma_.fixed = is_sigma_fixed
            elif isinstance(sigma_fixed, bool):
                sigma_.fixed = sigma_fixed
        return self_
