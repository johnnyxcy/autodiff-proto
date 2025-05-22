from __future__ import annotations

import typing

from sympy import Expr, Number, Symbol

from symbols._args import ParamArg, ParamArgWrt, ParamsArgRack
from symbols._symvar import SymVar
from symbols.to_cst import Cstifiable
from typings import Expression


class IntegralT(Symbol):
    pass


INTEGRAL_T: typing.Final[IntegralT] = IntegralT("__t")


class DADt(Symbol):
    """Class of compartment dAdt.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dAdt.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> DADt:
        name = f"dA_{cmt.name}dt"
        instance = typing.cast(DADt, super().__new__(cls, name))
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


class Alag(Symbol):
    """Class of compartment absorption lag.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of absorption lag.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> Alag:
        name = f"Alag_{cmt.name}"
        instance = typing.cast(Alag, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of absorption lag."""
        return self._expr


class Fraction(Symbol):
    """Class of compartment bioavailability fraction.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of bioavailability fraction.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> Fraction:
        name = f"Frac_{cmt.name}"
        instance = typing.cast(Fraction, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 1.0
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of bioavailability fraction."""
        return self._expr


class Rate(Symbol):
    """Class of compartment dose rate.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dose rate.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> Rate:
        name = f"R_{cmt.name}"
        instance = typing.cast(Rate, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of dose rate."""
        return self._expr


class Duration(Symbol):
    """Class of compartment dose duration.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    expr : Expression
        Expression of dose duration.
    """

    __slots__ = ("_cmt", "_expr")

    def __new__(cls, cmt: Compartment) -> Duration:
        name = f"D_{cmt.name}"
        instance = typing.cast(Duration, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of dose duration."""
        return self._expr


class CmtInitialA(Symbol):
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
        name = f"A0_{cmt.name}"
        instance = typing.cast(CmtInitialA, super().__new__(cls, name))
        instance._cmt = cmt
        instance._expr = 0.0
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt

    @property
    def expr(self) -> Expression:
        """Expression: Expression of initial amount."""
        return self._expr


class CmtSolvedA(Symbol):
    """Class of solved compartment amounts.

    Attributes
    ----------
    cmt : Compartment
        Corresponding compartment.
    """

    __slots__ = "_cmt"

    def __new__(cls, cmt: Compartment) -> CmtSolvedA:
        name = f"A_{cmt.name}"
        instance = typing.cast(CmtSolvedA, super().__new__(cls, name))
        instance._cmt = cmt
        return instance

    @property
    def cmt(self) -> Compartment:
        """Compartment: Corresponding compartment."""
        return self._cmt


class AWrt(Symbol):
    __slots__ = ("_cmt", "_wrt", "_wrt2nd")

    def __new__(
        cls, cmt: Compartment, wrt: SymVar, wrt2nd: SymVar | None = None
    ) -> AWrt:
        name = f"dA_{cmt.name}_d{wrt.name}"
        if wrt2nd:
            name += f"_d{wrt2nd.name}"
        instance = typing.cast(AWrt, super().__new__(cls, name))
        instance._cmt = cmt
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    @property
    def wrt(self) -> SymVar:
        return self._wrt

    @property
    def wrt2nd(self) -> SymVar | None:
        return self._wrt2nd


class DADtWrt(Symbol):
    __slots__ = ("_cmt", "_wrt", "_wrt2nd")

    @typing.overload
    def __new__(
        cls, cmt: Compartment, wrt: SymVar, wrt2nd: SymVar | None = None
    ) -> DADtWrt: ...

    @typing.overload
    def __new__(cls, cmt: Compartment, wrt: CmtSolvedA) -> DADtWrt: ...

    def __new__(
        cls, cmt: Compartment, wrt: SymVar | CmtSolvedA, wrt2nd: SymVar | None = None
    ) -> DADtWrt:
        if isinstance(wrt, CmtSolvedA):
            wrt_name = wrt.cmt.name
        else:
            wrt_name = wrt.name
        name = f"dA_{cmt.name}dt_d{wrt_name}"
        if wrt2nd:
            name += f"_d{wrt2nd.name}"
        instance = typing.cast(DADtWrt, super().__new__(cls, name))
        instance._cmt = cmt
        instance._wrt = wrt
        instance._wrt2nd = wrt2nd
        return instance

    @property
    def cmt(self) -> Compartment:
        return self._cmt

    @property
    def wrt(self) -> SymVar | CmtSolvedA:
        return self._wrt

    @property
    def wrt2nd(self) -> SymVar | None:
        return self._wrt2nd


class Compartment:
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
        self.__name = name
        self.__init_value = CmtInitialA(cmt=self)
        if init_value:
            self.__init_value._expr = init_value

        self.__default_dose = default_dose
        self.__default_obs = default_obs

        self.__dAdt = DADt(cmt=self)

        self.__alag = Alag(cmt=self)
        if alag is not None:
            self.__alag._expr = alag

        self.__fraction = Fraction(cmt=self)
        if fraction is not None:
            self.__fraction._expr = fraction

        self.__rate = Rate(cmt=self)
        if rate is not None:
            self.__rate._expr = rate

        self.__duration = Duration(cmt=self)
        if duration is not None:
            self.__duration._expr = duration

        self.__A = CmtSolvedA(cmt=self)

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
        return self.__A

    @property
    def dAdt(self) -> DADt:
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
        return self.__dAdt

    @dAdt.setter
    def dAdt(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()

        self.__dAdt._expr = val

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
        return self.__name

    @name.setter
    def name(self, val: str) -> None:
        self.__name = val
        self.__A.name = f"A_{val}"
        self.__dAdt.name = f"dA_{val}dt"
        self.__alag.name = f"Alag_{val}"
        self.__fraction.name = f"Fraction_{val}"
        self.__rate.name = f"Rate_{val}"
        self.__duration.name = f"Duration_{val}"

    @property
    def alag(self) -> Alag:
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
        return self.__alag

    @alag.setter
    def alag(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self.__alag._expr = val

    @property
    def fraction(self) -> Fraction:
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
        return self.__fraction

    @fraction.setter
    def fraction(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self.__fraction._expr = val

    @property
    def rate(self) -> Rate:
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
        return self.__rate

    @rate.setter
    def rate(self, val: Expression) -> None:
        if not isinstance(val, Expression):
            raise TypeError()
        self.__rate._expr = val

    @property
    def duration(self) -> Duration:
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
        return self.__duration

    @duration.setter
    def duration(self, val: Expression) -> None:
        if not isinstance(val, Expression):
            raise TypeError()
        self.__duration._expr = val

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
        return self.__init_value

    @init_value.setter
    def init_value(self, val: Expression) -> None:
        if not isinstance(val, int | float | Expr):
            raise TypeError()
        self.__init_value._expr = val

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
        return self.__default_dose

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
        return self.__default_obs

    def __getitem__(
        self, __key: str | tuple[str, SymVar] | tuple[str, SymVar, SymVar]
    ) -> ParamArg | ParamArgWrt:
        return ParamsArgRack()[__key]
