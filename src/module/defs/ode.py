from __future__ import annotations

import typing

import libcst as cst
import pydantic

from module.defs.module import Module, ModuleMetaclass
from symbols._cmt import INTEGRAL_T, Compartment, IntegralT
from typings import CodeGen


class odeint:
    """Class of ODE solver."""

    class _internal:
        class OdeintSettings(pydantic.BaseModel):
            def as_configuration_dict(self) -> dict[str, typing.Any]:
                """Convert the settings to a configuration dictionary."""
                raise NotImplementedError(
                    "This method should be implemented in subclasses"
                )

        class DVERKSettings(OdeintSettings):
            tol: float = pydantic.Field(
                default=1e-6, ge=1e-12, le=1e-2, allow_inf_nan=False
            )
            err_typ: typing.Literal["absolute", "relative", "combined"] = "combined"
            floor: float = pydantic.Field(
                default=1e-5, ge=1e-12, le=1e-2, allow_inf_nan=False
            )
            max_fun_calls: int = pydantic.Field(ge=0, le=1000000)

            def as_configuration_dict(self) -> dict[str, typing.Any]:
                """Convert the settings to a configuration dictionary."""
                return {
                    "odeint.solver": "dverk",
                    "odeint.dverk.tol": self.tol,
                    "odeint.dverk.err_typ": self.err_typ,
                    "odeint.dverk.floor": self.floor,
                    "odeint.dverk.max_fun_calls": self.max_fun_calls,
                }

        class LSODASettings(OdeintSettings):
            rel_tol: float = pydantic.Field(
                default=1e-12, ge=1e-12, le=1e-2, allow_inf_nan=False
            )
            abs_tol: float = pydantic.Field(
                default=1e-12, ge=1e-12, le=1e-2, allow_inf_nan=False
            )
            max_steps: int = pydantic.Field(default=500, gt=0, le=10000)

            def as_configuration_dict(self) -> dict[str, typing.Any]:
                """Convert the settings to a configuration dictionary."""
                return {
                    "odeint.solver": "lsoda",
                    "odeint.lsoda.rel_tol": self.rel_tol,
                    "odeint.lsoda.abs_tol": self.abs_tol,
                    "odeint.lsoda.max_steps": self.max_steps,
                }

    @staticmethod
    def DVERK(
        tol: float = 1e-6,
        err_typ: typing.Literal["absolute", "relative", "combined"] = "combined",
        floor: float = 0.00001,
        max_fun_calls: int = 100000,
    ) -> _internal.DVERKSettings:
        """Verner's fifth and sixth order Runge-Kutta method for approximating solutions
        to first order ordinary differential equations with initial conditions.

        Parameters
        ----------
        tol : float, optional
            Tolerance. Defaults to `1e-6`.
        err_typ : typing.Literal["absolute", "relative", "combined"], optional
            If `"absolute"`, will use absolute error control, where error weights are set to 1.
            If `"relative"`, will use relative error control, where error weights are set to :math:`1/abs(y(k))`.
            If `"combined"`, will use combined error control, where error weights are set to :math:`1/max(abs(y(k))` or :math:`1/max(abs(floor)` if :math:`abs(y(k))` is less than the floor value :math:`abs(floor)`. See also arguments `floor`.
            Defaults to `"combined"`.
        floor: float, optional
            Floor value to use, when `err_typ="combined"`.
            Defaults to `0.00001`.
        max_fun_calls: int, optional
            Maximum number of function evaluations. Defaults to `100000`.

        Returns
        -------
        DVERKSettings
            Solver settings.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__(solver=odeint.DVERK(tol=1e-9))

        References
        ----------
        Hull, T. & Enright, W.H. & Jackson, Kenneth. (1976). User's guide for DVERK-a subroutine
        for solving non-stiff ODEs.

        """
        return odeint._internal.DVERKSettings(
            tol=tol, err_typ=err_typ, floor=floor, max_fun_calls=max_fun_calls
        )

    @staticmethod
    def LSODA(
        rel_tol: float = 1e-6, abs_tol: float = 1e-10, max_steps: int = 500
    ) -> _internal.LSODASettings:
        """LSODA algorithm from Linda Petzold and Alan Hindmarsh, which solves the initial value problem for
        stiff or nonstiff systems of first order ordinary differential equations.

        Parameters
        ----------
        rel_tol : float, optional
            Relative tolerance. Defaults to `1e-6`.
        abs_tol : float, optional
            Absolute tolerance. Defaults to `1e-10`.
        max_steps: int, optional
            Number of steps to take. Defaults to `500`

        Returns
        -------
        LSODASettings
            Solver settings.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__(solver=odeint.LSODA(rel_tol=1e-9, abs_tol=1e-9))

        References
        ----------
        Petzold, L. . (1983). Automatic selection of methods for solving stiff and nonstiff systems of
        ordinary differential equations. Siam J.sci.stat.comput, 4(1), 136-148.
        """
        return odeint._internal.LSODASettings(
            rel_tol=rel_tol, abs_tol=abs_tol, max_steps=max_steps
        )


AnyOdeSolverConfiguration = (
    odeint._internal.OdeintSettings
    | typing.Callable[[], odeint._internal.OdeintSettings]
)


class OdeModule(Module, metaclass=ModuleMetaclass):
    """Module for building ordinary differential equation models.

    Attributes
    ----------
    t : IntegralT
        A symbol represents the timestamp in computation stage for ordinary differential equations.

    Examples
    --------
    Build a pk-pd model using compartment system and ordinary differential equations.

    >>>    class TestModel(OdeModule):
    >>>        def __init__(self):
    >>>            super().__init__(solver=odeint.LSODA(rel_tol=1e-9, abs_tol=1e-9))
    >>>            self.cmt_gut = compartment(default_dose=True)
    >>>            self.cmt_central = compartment(default_obs=True)
    >>>            self.cmt_eff = compartment()
    >>>            self.cl = theta(0.1, bounds=(0, None))
    >>>            self.v = theta(8, bounds=(0, None))
    >>>            self.ka = theta(1.5, bounds=(0, None))
    >>>            self.alag = theta(1, bounds=(0, None))
    >>>            self.eo = theta(95, bounds=(0, None))
    >>>            self.emax = theta(-250, bounds=(-500, 0))
    >>>            self.ec50 = theta(11.0, bounds=(0, None))
    >>>            self.keo = theta(0.02, bounds=(0, None))
    >>>            self.eta_cl = omega(0.06)
    >>>            self.eta_v = omega(0.02)
    >>>            self.eta_ka = omega(0.4)
    >>>            self.eta_alag = omega(0.3)
    >>>            self.eta_e0 = omega(0.002)
    >>>            self.eta_emax = omega(0, fixed=True)
    >>>            self.eta_ec50 = omega(0.04)
    >>>            self.eta_ke0 = omega(0.06)
    >>>            self.eps_prop_pk = sigma(0.001)
    >>>            self.eps_add_pk = sigma(0.64)
    >>>            self.eps_add_pd = sigma(14)
    >>>            self.wt = column("WT")
    >>>            self.dvid = column("DVID")
    >>>
    >>>        def pred(self):
    >>>            cl = self.cl * (self.WT / 70) ** 0.75 * exp(self.eta_cl)
    >>>            v = self.v * (self.WT / 70) * exp(self.eta_v)
    >>>            ka = self.ka * exp(self.eta_ka)
    >>>            alag = self.alag * exp(self.eta_alag)
    >>>            self.cmt_gut.alag = alag
    >>>            k20 = cl / v
    >>>            e0 = self.eo * exp(self.eta_e0)
    >>>            emax = self.emax * exp(self.eta_emax)
    >>>            ec50 = self.ec50 * exp(self.eta_ec50)
    >>>            ke0 = self.keo * exp(self.eta_ke0)
    >>>            self.cmt_gut.dAdt = (-ka) * self.cmt_gut.A
    >>>            self.cmt_central.dAdt = ka * self.cmt_gut.A - k20 * self.cmt_central.A
    >>>            self.cmt_eff.dAdt = ke0 * (self.cmt_central.A / v - self.cmt_eff.A)
    >>>            conc_central = self.cmt_central.A / v
    >>>            conc_eff = self.cmt_eff.A
    >>>            eff = e0 + emax * conc_eff / (ec50 + conc_eff)
    >>>            if (self.DVID <= 1):
    >>>                ipred = conc_central
    >>>                y = conc_central * (1 + self.eps_prop_pk) + self.eps_add_pk
    >>>            else:
    >>>                ipred = eff
    >>>                y = eff + self.eps_add_pd
    >>>            return y
    """

    def __init__(self, solver: AnyOdeSolverConfiguration = odeint.DVERK) -> None:
        """Build a ODE model.

        Parameters
        ----------
        solver : AnyOdeSolverConfiguration, optional
            ODE solver and related settings. Supported solver are `odeint.DVERK` and `odeint.LSODA`.
            Defaults to `odeint.DVERK`.

        Examples
        --------
        >>>    class TestModel(OdeModule):
        >>>        def __init__(self):
        >>>            super().__init__(solver=odeint.LSODA(rel_tol=1e-9, abs_tol=1e-9))
        >>>            ...
        """
        super().__init__()

        if isinstance(solver, typing.Callable):
            solver = solver()

        # use setattr since we do not want user to get access to this property
        setattr(self, "_solver_", solver)

    @property
    def t(self) -> IntegralT:
        """IntegralT: A symbolic `t` which represents the timestamp in computation stage for ordinary differential equations"""
        return INTEGRAL_T

    def __post_init__(self) -> None:
        super().__post_init__()

        namespace = self.__dict__
        any_is_cmt = False
        for variable_name, variable_obj in namespace.items():
            if isinstance(variable_obj, Compartment):
                variable_obj.name = variable_name
                any_is_cmt = True

            if variable_name == "t" and variable_obj is not self.t:
                raise ValueError("Invalid t assignment")

        if not any_is_cmt:
            raise AssertionError(
                "You must define at least one Compartment to use OdeModule"
            )


OdeModuleT = typing.TypeVar("OdeModuleT", bound=OdeModule, default=typing.Any)


def get_solver(
    module: OdeModule,
) -> odeint._internal.OdeintSettings:
    """Get the ODE solver settings from the module.

    Parameters
    ----------
    module : OdeModule
        The ODE module to get the solver settings from.

    Returns
    -------
    odeint._internal.OdeintSettings
        The ODE solver settings.

    Examples
    --------
    >>> model = TestModel()
    >>> solver = get_solver(model)
    """
    solver = getattr(module, "_solver_", odeint.DVERK())
    if isinstance(solver, typing.Callable):
        solver = solver()
    if not isinstance(solver, odeint._internal.OdeintSettings):
        raise TypeError(
            f"Invalid solver type {type(solver)}, expected `odeint._internal.OdeintSettings` or a callable returning it"
        )
    return solver
