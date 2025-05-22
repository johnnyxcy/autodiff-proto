import typing

from sympy import Expr, exp

exp1 = exp


@typing.overload
def normal_cdf(x: Expr) -> Expr: ...
@typing.overload
def normal_cdf(x: float) -> float: ...


def normal_cdf(x: Expr | float) -> Expr | float:
    A1 = 0.31938153
    A2 = -0.356563782
    A3 = 1.781477937
    A4 = -1.821255978
    A5 = 1.330274429
    RSQRT2PI = 0.39894228040143267793994605993438

    abs_x = x
    if x < 0:
        abs_x = -x

    K = 1.0 / (1.0 + 0.2316419 * abs_x)
    K4 = A4 + K * A5
    K3 = A3 + K * K4
    K2 = A2 + K * K3
    K1 = A1 + K * K2
    cnd = RSQRT2PI * exp1(-0.5 * x * x) * (K * K1)

    if x >= 0:
        cnd = 1 - cnd

    return cnd
