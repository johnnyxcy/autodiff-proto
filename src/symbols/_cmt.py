from __future__ import annotations

import typing
from uuid import uuid4

import libcst as cst
from sympy import Expr, Number, Symbol

from symbols._args import ParamArg, ParamArgWrt
from typings import AsCSTExpression, CodeGen, Expression, ValueType


class IntegralT(Symbol):
    pass


INTEGRAL_T: typing.Final[IntegralT] = IntegralT("__t")


class CmtDosingParamSymbol(Symbol, AsCSTExpression):
    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to return the parameter name."
        )

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        raise NotImplementedError(
            "This method should be implemented in subclasses to return the corresponding compartment."
        )

    def as_param_arg(self) -> CmtParamArg:
        """Convert the CmtDosingParamSymbol object to a CmtParamArg."""
        return CmtParamArg(param_name=self.param_name, cmt=self.cmt)

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the CmtDosingParamSymbol object to a CST expression.
        """
        return self.as_param_arg().as_cst_expression()


class CmtAlag(CmtDosingParamSymbol):
    """Class of compartment absorption lag.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of absorption lag.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtAlag:
        name = f"__Alag_{{{cmt.name}}}"
        instance = typing.cast(CmtAlag, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        return "ALAG"

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of absorption lag."""
        return self._expr


class CmtFraction(CmtDosingParamSymbol):
    """Class of compartment bioavailability fraction.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of bioavailability fraction.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtFraction:
        name = f"__Fraction_{{{cmt.name}}}"
        instance = typing.cast(CmtFraction, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 1.0
        return instance

    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        return "FRACTION"

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of bioavailability fraction."""
        return self._expr


class CmtRate(CmtDosingParamSymbol):
    """Class of compartment dose rate.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dose rate.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtRate:
        name = f"__Rate_{{{cmt.name}}}"
        instance = typing.cast(CmtRate, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        return "RATE"

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of dose rate."""
        return self._expr


class CmtDuration(CmtDosingParamSymbol):
    """Class of compartment dose duration.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dose duration.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtDuration:
        name = f"__Duration_{{{cmt.name}}}"
        instance = typing.cast(CmtDuration, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        return "DURATION"

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of dose duration."""
        return self._expr


class CmtInitialA(CmtDosingParamSymbol):
    """Class of initial compartment amounts.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of initial compartment amount.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtInitialA:
        name = f"__A0_{{{cmt.name}}}"
        instance = typing.cast(CmtInitialA, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def param_name(self) -> str:
        """str: Name of the parameter."""
        return "A0"

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of initial amount."""
        return self._expr


class CmtSolvedA(Symbol, AsCSTExpression):
    """Class of solved compartment amounts.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    """

    __slots__ = "_cmt"

    def __new__(cls, cmt: Compartment) -> CmtSolvedA:
        name = f"__A_{{{cmt.name}}}"
        instance = typing.cast(CmtSolvedA, super().__new__(cls, name))
        instance._cmt = cmt
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the CmtSolvedA object to a CST expression.
        """

        return cst.Subscript(
            value=cst.Name(CmtSolvedARack.name),
            slice=[
                cst.SubscriptElement(
                    slice=cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.cmt.name),
                        )
                    ),
                ),
            ],
        )


class CmtSolvedAWrt(Symbol, AsCSTExpression):
    __slots__ = ("_cmt", "_wrt", "_wrt2nd")

    def __new__(
        cls, cmt: Compartment, wrt: Symbol, wrt2nd: Symbol | None = None
    ) -> CmtSolvedAWrt:
        if wrt2nd is not None:
            name = f"∂²A_{{{cmt.name}}}/∂{wrt.name}∂{wrt2nd.name}"
        else:
            name = f"∂A_{{{cmt.name}}}/∂{wrt.name}"
        instance = typing.cast(CmtSolvedAWrt, super().__new__(cls, name))
        instance._cmt = cmt
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the CmtSolvedAWrt object to a CST expression.
        """
        slice = [
            cst.SubscriptElement(
                slice=cst.Index(
                    cst.Attribute(
                        value=cst.Name("self"),
                        attr=cst.Name(self.cmt.name),
                    )
                ),
            ),
        ]
        if isinstance(self.wrt, AsCSTExpression):
            wrt1st = cst.SubscriptElement(
                cst.Index(self.wrt.as_cst_expression()),
            )
        else:
            wrt1st = cst.SubscriptElement(
                cst.Index(
                    cst.Attribute(
                        value=cst.Name("self"),
                        attr=cst.Name(self.wrt.name),
                    )
                )
            )
        slice.append(wrt1st)

        if self.wrt2nd is not None:
            if isinstance(self.wrt2nd, AsCSTExpression):
                wrt2nd = cst.SubscriptElement(
                    cst.Index(self.wrt2nd.as_cst_expression()),
                )
            else:
                wrt2nd = cst.SubscriptElement(
                    cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.wrt2nd.name),
                        )
                    )
                )
            slice.append(wrt2nd)

        return cst.Subscript(value=cst.Name(CmtSolvedARack.name), slice=slice)


class CmtSolvedARack:
    """
    Representing a dummy getter for the amounts of any arbitrary compartment to be used in MTran.
    """

    name = "__A__"

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, key: Compartment) -> CmtSolvedA:
        """Get the amount in the compartment at time `t`."""
        ...

    @typing.overload
    def __getitem__(
        self, key: tuple[Compartment, Symbol] | tuple[Compartment, Symbol, Symbol]
    ) -> CmtSolvedAWrt:
        """Get the derivative of amount in the compartment with respect to a variable."""
        ...

    def __getitem__(
        self,
        key: Compartment
        | tuple[Compartment, Symbol]
        | tuple[Compartment, Symbol, Symbol],
    ) -> CmtSolvedA | CmtSolvedAWrt:
        if isinstance(key, tuple):
            if len(key) == 2:  # first order
                cmt, wrt = key
                return CmtSolvedAWrt(cmt=cmt, wrt=wrt)
            else:  # second order
                cmt, wrt, wrt2nd = key
                return CmtSolvedAWrt(cmt=cmt, wrt=wrt, wrt2nd=wrt2nd)
        else:
            return key.A


class CmtDADt(Symbol, AsCSTExpression):
    """Class of compartment dAdt.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dAdt.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> CmtDADt:
        name = f"__dA_{{{cmt.name}}}dt"
        instance = typing.cast(CmtDADt, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = Number(0.0)
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of dAdt."""
        return self._expr

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the CmtDADt object to a CST expression.
        """

        return cst.Subscript(
            value=cst.Name(CmtDADtTransRack.name),
            slice=[
                cst.SubscriptElement(
                    slice=cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.cmt.name),
                        )
                    ),
                ),
            ],
        )


class CmtDADtWrt(Symbol, AsCSTExpression):
    __slots__ = ("_cmt", "_wrt", "_wrt2nd")

    def __new__(
        cls, cmt: Compartment, wrt: Symbol, wrt2nd: Symbol | None = None
    ) -> CmtDADtWrt:
        if wrt2nd is not None:
            name = f"∂²dA_{{{cmt.name}}}dt/∂{wrt.name}∂{wrt2nd.name}"
        else:
            name = f"∂dA_{{{cmt.name}}}dt/∂{wrt.name}"
        instance = typing.cast(CmtDADtWrt, super().__new__(cls, name))
        instance._cmt = cmt
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    @property
    def wrt(self) -> Symbol:
        return self._wrt

    @property
    def wrt2nd(self) -> Symbol | None:
        return self._wrt2nd

    def as_cst_expression(self) -> cst.BaseExpression:
        """
        Convert the CmtDADtWrt object to a CST expression.
        """
        slice = [
            cst.SubscriptElement(
                slice=cst.Index(
                    cst.Attribute(
                        value=cst.Name("self"),
                        attr=cst.Name(self.cmt.name),
                    )
                ),
            ),
        ]
        if isinstance(self.wrt, AsCSTExpression):
            wrt1st = cst.SubscriptElement(
                cst.Index(self.wrt.as_cst_expression()),
            )
        else:
            wrt1st = cst.SubscriptElement(
                cst.Index(
                    cst.Attribute(
                        value=cst.Name("self"),
                        attr=cst.Name(self.wrt.name),
                    )
                )
            )
        slice.append(wrt1st)

        if self.wrt2nd is not None:
            if isinstance(self.wrt2nd, AsCSTExpression):
                wrt2nd = cst.SubscriptElement(
                    cst.Index(self.wrt2nd.as_cst_expression()),
                )
            else:
                wrt2nd = cst.SubscriptElement(
                    cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.wrt2nd.name),
                        )
                    )
                )
            slice.append(wrt2nd)

        return cst.Subscript(value=cst.Name(CmtDADtTransRack.name), slice=slice)


class CmtDADtTransRack:
    """
    Representing a dummy getter for the dAdt and corresponding derivatives of any arbitrary compartment to be used in MTran.
    """

    name = "__DADT__"

    def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, key: Compartment) -> CmtDADt: ...

    @typing.overload
    def __getitem__(
        self,
        key: tuple[Compartment, Symbol | CmtSolvedA]
        | tuple[Compartment, Symbol, Symbol],
    ) -> CmtDADtWrt: ...

    def __getitem__(
        self,
        key: Compartment
        | tuple[Compartment, Symbol | CmtSolvedA]
        | tuple[Compartment, Symbol, Symbol],
    ) -> CmtDADt | CmtDADtWrt:
        if isinstance(key, tuple):
            if len(key) == 2:  # first order
                cmt, wrt = key
                return CmtDADtWrt(cmt=cmt, wrt=wrt)
            else:  # second order
                cmt, wrt, wrt2nd = key
                return CmtDADtWrt(cmt=cmt, wrt=wrt, wrt2nd=wrt2nd)
        else:
            return key.dAdt


class CmtParamArg(ParamArg):
    def __init__(self, param_name: str, cmt: Compartment) -> None:
        super().__init__(param_name)
        self._cmt = cmt

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    def as_cst_expression(self) -> cst.BaseExpression:
        return cst.Subscript(
            value=cst.Name(CmtParamArgTransRack.name),
            slice=[
                cst.SubscriptElement(
                    slice=cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.cmt.name),
                        )
                    ),
                ),
                *self._as_cst_slices(),
            ],
        )

    def diff(self, wrt: Symbol, wrt2nd: Symbol | None = None) -> ParamArgWrt:
        """
        Returns a derivative of the parameter argument with respect to a variable.
        This is a placeholder method and should be implemented in subclasses.
        """
        return CmtParamArgWrt(
            cmt=self.cmt, param_name=self.param_name, wrt=wrt, wrt2nd=wrt2nd
        )


class CmtParamArgWrt(ParamArgWrt):
    def __init__(
        self,
        param_name: str,
        cmt: Compartment,
        wrt: Symbol,
        wrt2nd: Symbol | None = None,
    ) -> None:
        super().__init__(param_name, wrt, wrt2nd)
        self._cmt = cmt

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    def as_cst_expression(self) -> cst.BaseExpression:
        return cst.Subscript(
            value=cst.Name(CmtParamArgTransRack.name),
            slice=[
                cst.SubscriptElement(
                    slice=cst.Index(
                        cst.Attribute(
                            value=cst.Name("self"),
                            attr=cst.Name(self.cmt.name),
                        )
                    ),
                ),
                *self._as_cst_slices(),
            ],
        )


class Compartment(CodeGen):
    """Class of compartments.

    Attributes
    ----------
    name : str
        Name of the compartment.
    A : CmtSolvedA
        Amount in the compartment at time `t`.
    dAdt : DADt
        Derivative with respect to time `t` of the amount in compartment.
    init_value : CmtInitialA
        Expression of initial amount for the compartment.
    alag : Alag
        Expression of absorption lag for the compartment.
    fraction : Fraction
        Expression of bioavailability fraction for the compartment.
    rate : Rate
        Expression of dose rate for the compartment.
    duration : Duration
        Expression of dose duration for the compartment.
    default_dose : bool
        Whether the compartment is default dose compartment.
    default_obs : bool
        Whether the compartment is default observation compartment.
    """

    def __init__(
        self,
        name: str,
        init_value: float | None = None,
        default_dose: bool = False,
        default_obs: bool = False,
        alag: float | None = None,
        fraction: float | None = None,
        rate: float | None = None,
        duration: float | None = None,
    ) -> None:
        self._name = name
        self._init_value = CmtInitialA(cmt=self)
        if init_value:
            self._init_value._expr = init_value

        self._default_dose = default_dose
        self._default_obs = default_obs

        self._dAdt = CmtDADt(cmt=self)

        self._alag = CmtAlag(cmt=self)
        if alag is not None:
            self._alag._expr = alag

        self._fraction = CmtFraction(cmt=self)
        if fraction is not None:
            self._fraction._expr = fraction

        self._rate = CmtRate(cmt=self)
        if rate is not None:
            self._rate._expr = rate

        self._duration = CmtDuration(cmt=self)
        if duration is not None:
            self._duration._expr = duration

        self._A = CmtSolvedA(cmt=self)

    def __deepcopy__(self, memo: typing.Any) -> Compartment:
        return Compartment(
            name=self._name,
            init_value=self._init_value._expr,
            default_dose=self.default_dose,
            default_obs=self.default_obs,
            alag=self.alag._expr,
            fraction=self._fraction._expr,
            rate=self._rate._expr,
            duration=self._duration._expr,
        )

    def _code_gen(self):
        args: list[cst.Arg] = []

        if self._default_dose:
            args.append(
                cst.Arg(
                    keyword=cst.Name("default_dose"),
                    value=cst.Name(value="True"),
                )
            )

        if self._default_obs:
            args.append(
                cst.Arg(
                    keyword=cst.Name("default_obs"),
                    value=cst.Name(value="True"),
                )
            )

        def should_explicit_declare(expr: Expression, default_value: float) -> bool:
            """Check if the expression is a constant."""
            return expr != default_value

        if should_explicit_declare(self._init_value.expr, 0.0):
            args.append(
                cst.Arg(
                    keyword=cst.Name("init_value"),
                    value=cst.Float(value=str(self._init_value._expr)),
                )
            )
        if should_explicit_declare(self._alag.expr, 0.0):
            args.append(
                cst.Arg(
                    keyword=cst.Name("alag"),
                    value=cst.Float(value=str(self._alag._expr)),
                )
            )
        if should_explicit_declare(self._fraction.expr, 1.0):
            args.append(
                cst.Arg(
                    keyword=cst.Name("fraction"),
                    value=cst.Float(value=str(self._fraction._expr)),
                )
            )
        return cst.Assign(
            targets=[cst.AssignTarget(cst.Name(value=self.name))],
            value=cst.Call(func=cst.Name(value=compartment.__name__), args=args),
        )

    @property
    def A(self) -> CmtSolvedA:
        """CmtSolvedA: Amount in the compartment at time `t`.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         self.ka = theta(1.0, bounds=(0, None))
        >>>         self.eta_ka = omega(0.04)
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         ka = self.ka * exp(self.eta_ka)
        >>>         self.cmt_depot.dAdt = (-ka) * self.cmt_depot.A
        >>>         ...
        """
        return self._A

    @property
    def dAdt(self) -> CmtDADt:
        """DADt: Derivative with respect to time `t` of the amount in compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         self.ka = theta(1.0, bounds=(0, None))
        >>>         self.eta_ka = omega(0.04)
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         ka = self.ka * exp(self.eta_ka)
        >>>         self.cmt_depot.dAdt = (-ka) * self.cmt_depot.A
        >>>         ...
        """
        return self._dAdt

    @dAdt.setter
    def dAdt(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()

        self._dAdt._expr = val

    @property
    def name(self) -> str:
        """str: Name of the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         ...
        >>> model = TestModel()
        >>> model.cmt_depot.name
        cmt_depot
        """
        return self._name

    @name.setter
    def name(self, val: str) -> None:
        self._name = val
        self._A.name = f"__A_{val}"
        self._dAdt.name = f"__dA_{val}dt"
        self._alag.name = f"__Alag_{val}"
        self._fraction.name = f"__Fraction_{val}"
        self._rate.name = f"__Rate_{val}"
        self._duration.name = f"__Duration_{val}"

    @property
    def alag(self) -> CmtAlag:
        """Alag: Expression of absorption lag for the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         self.alag = theta(1.5, bounds=(0, None))
        >>>         self.eta_alag = omega(0.02)
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         alag = self.alag * exp(self.eta_alag)
        >>>         self.cmt_depot.alag = alag
        >>>         self.cmt_depot.dAdt = (-ka) * self.cmt_depot.A
        >>>         ...
        """
        return self._alag

    @alag.setter
    def alag(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self._alag._expr = val

    @property
    def fraction(self) -> CmtFraction:
        """Fraction: Expression of bioavailability fraction for the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         self.frac = theta(0.9, bounds=(0, 1))
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         self.cmt_depot.fraction = self.frac
        >>>         self.cmt_depot.dAdt = (-ka) * self.cmt_depot.A
        >>>         ...
        """
        return self._fraction

    @fraction.setter
    def fraction(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self._fraction._expr = val

    @property
    def rate(self) -> CmtRate:
        """Rate: Expression of dose rate for the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_central = compartment(init_value=0, default_dose=True, default_obs=True)
        >>>         self.k = theta(0.5, bounds(0, None))
        >>>         self.eta_k = omega(0.02)
        >>>         self.rate = column["RATE"]
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         k = self.k * exp(self.eta_k)
        >>>         self.cmt_central.rate = self.rate
        >>>         self.cmt_central.dAdt = -k * self.cmt_central.A
        >>>         ...
        """
        return self._rate

    @rate.setter
    def rate(self, val: Expression) -> None:
        if not isinstance(val, Expression):
            raise TypeError()
        self._rate._expr = val

    @property
    def duration(self) -> CmtDuration:
        """Duration: Expression of dose duration for the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_central = compartment(init_value=0, default_dose=True, default_obs=True)
        >>>         self.k = theta(0.5, bounds(0, None))
        >>>         self.eta_k = omega(0.02)
        >>>         self.dur = column["DUR"]
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         k = self.k * exp(self.eta_k)
        >>>         self.cmt_central.duration = self.dur
        >>>         self.cmt_central.dAdt = -k * self.cmt_central.A
        >>>         ...
        """
        return self._duration

    @duration.setter
    def duration(self, val: Expression) -> None:
        if not isinstance(val, Expression):
            raise TypeError()
        self._duration._expr = val

    @property
    def init_value(self) -> CmtInitialA:
        """CmtInitialA: Expression of initial amount for the compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_central = compartment(default_dose=True, default_obs=True)
        >>>         self.k = theta(0.5, bounds(0, None))
        >>>         self.eta_k = omega(0.02)
        >>>         self.init_amt = column["INITS"]
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         k = self.k * exp(self.eta_k)
        >>>         self.cmt_central.init_value = self.init_amt
        >>>         self.cmt_central.dAdt = -k * self.cmt_central.A
        >>>         ...
        """
        return self._init_value

    @init_value.setter
    def init_value(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self._init_value._expr = val

    @property
    def default_dose(self) -> bool:
        """bool: Whether the compartment is default dose compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         ...
        >>> model = TestModel()
        >>> model.cmt_depot.default_dose
        True
        """
        return self._default_dose

    @property
    def default_obs(self) -> bool:
        """bool: Whether the compartment is default observation compartment.

        Examples
        --------
        >>> class TestModel(OdeModule):
        >>>     def __init__(self):
        >>>         super().__init__()
        >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
        >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
        >>>         ...
        >>> model = TestModel()
        >>> model.cmt_central.default_obs
        True
        """
        return self._default_obs


class CmtParamArgTransRack:
    """A rack for compartment parameter arguments.

    This class is used to create and manage compartment parameter arguments.
    It allows access to compartment parameters by their names or by their names
    and the variables they are differentiated with respect to.
    """

    name: str = "__CMTP__"

    def __setitem__(self, __key: typing.Any, __value: typing.Any) -> None:
        raise NotImplementedError()

    @typing.overload
    def __getitem__(self, __cmt: Compartment, __name: str) -> CmtParamArg:
        """Get a parameter argument by its name."""
        ...

    @typing.overload
    def __getitem__(
        self,
        __cmt: Compartment,
        __name: str,
        __wrt: Symbol,
        __wrt2nd: Symbol | None = None,
    ) -> CmtParamArgWrt:
        """Get a parameter argument derivative with respect to a variable."""
        ...

    def __getitem__(
        self,
        __cmt: Compartment,
        __name: str,
        __wrt: Symbol | None = None,
        __wrt2nd: Symbol | None = None,
    ) -> CmtParamArg | CmtParamArgWrt:
        if __wrt is not None:
            return CmtParamArgWrt(
                param_name=__name,
                cmt=__cmt,
                wrt=__wrt,
                wrt2nd=__wrt2nd,
            )
        else:
            return CmtParamArg(param_name=__name, cmt=__cmt)


def compartment(
    init_value: ValueType = 0.0,
    alag: ValueType = 0.0,
    fraction: ValueType = 1.0,
    default_dose: bool = False,
    default_obs: bool = False,
) -> Compartment:
    """Create a single compartment.

    Parameters
    ----------
    init_value : ValueType, optional
        Initial amount for the compartment. Defaults to `0`.
    alag : ValueType, optional
        Absorption lag for the compartment. Defaults to `0`.
    fraction : ValueType, optional
        Bioavailability fraction for the compartment. Defaults to `1`.
    default_dose : bool, optional
        Whether the compartment is default dose compartment. Defaults to `False`.
    default_obs : bool, optional
        Whether the compartment is default observation compartment. Defaults to `False`.

    Returns
    -------
    Compartment
        A compartment variable.

    Examples
    --------
    >>> class TestModel(OdeModule):
    >>>     def __init__(self):
    >>>         super().__init__()
    >>>         self.cmt_depot = compartment(init_value=0, default_dose=True, default_obs=False)
    >>>         self.cmt_central = compartment(init_value=0, default_dose=False, default_obs=True)
    >>>         self.cmt_effect = compartment(init_value=0, default_dose=False, default_obs=False)
    >>>         ...
    """
    name = f"__unnamed_cmt_{uuid4().hex}"

    return Compartment(
        name=name,
        alag=alag,
        fraction=fraction,
        init_value=init_value,
        default_dose=default_dose,
        default_obs=default_obs,
    )
