import sympy

from mas.libs.masmod.modeling.syntax.transformers.inline.flags import (
    never_inline_transpile,
)
from mas.libs.masmod.modeling.typings import Expression

__all__ = [
    "abs",
    "floor",
    "ceiling",
    "sqrt",
    "exp",
    "log",
    "ln",
    "log10",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "sinh",
    "cosh",
    "tanh",
]


def abs(expr: Expression) -> sympy.Expr:
    """Absolute value.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> abs(-1)
    1
    >>> abs(1)
    1
    >>> abs(x)
    abs(x)
    """
    return sympy.Abs(expr)


def floor(expr: Expression) -> sympy.Expr:
    """
    Floor value.

    Parameters
    ----------
    expr : Expression
        Expression.

    Returns
    -------
    sympy.Expr
        The greatest integer less than or equal to the input expression.

    Examples
    --------
    >>> floor(2.7)
    2
    >>> floor(-1.2)
    -2
    """
    return sympy.floor(expr)


def ceiling(expr: Expression) -> sympy.Expr:
    """
    Return the ceiling of the given expression.

    The ceiling of a number is the smallest integer greater than or equal to that number.

    Parameters
    ----------
    expr : Expression
        The input expression to compute the ceiling for.

    Returns
    -------
    sympy.Expr
        The ceiling of the input expression as a SymPy expression.

    Examples
    --------
    >>> ceiling(2.3)
    3
    >>> ceiling(-1.7)
    -1
    """
    return sympy.ceiling(expr)


def sqrt(expr: Expression) -> sympy.Expr:
    """Square root.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> sqrt(9)
    3
    """
    return expr ** (1 / 2)


# region exponential
def exp(expr: Expression) -> sympy.Expr:
    """The exponential function, :math:`e^x`.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> exp(x)
    exp(x)
    >>> exp(x).diff(x)
    exp(x)
    """
    return sympy.exp(expr)


def log(expr: Expression) -> sympy.Expr:
    """The natural logarithm function, :math:`ln(x)` or :math:`log(x)`.

    Logarithms are taken with the natural base, `e`.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> log(E)
    1
    """
    return sympy.log(expr)


def ln(expr: Expression) -> sympy.Expr:
    """The natural logarithm function, :math:`ln(x)`.

    Logarithms are taken with the natural base, `e`.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> ln(E)
    1
    """
    return log(expr)


def log10(expr: Expression) -> sympy.Expr:
    """The logarithm function :math:`log10(x)`.

    Logarithms are taken with the base, `10`.

    Parameters
    ----------
    expr : Expression
        Expression.

    Examples
    --------
    >>> log10(10)
    1
    """
    return sympy.log(expr, sympy.Number(10))


# endregion

# region trigonometric


def sin(expr: Expression) -> sympy.Expr:
    """
    Sine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Sine of the input expression.

    Examples
    --------
    >>> sin(0)
    0
    >>> sin(sympy.pi / 2)
    1
    """
    return sympy.sin(expr)


def cos(expr: Expression) -> sympy.Expr:
    """
    Cosine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Cosine of the input expression.

    Examples
    --------
    >>> cos(0)
    1
    >>> cos(sympy.pi)
    -1
    """
    return sympy.cos(expr)


def tan(expr: Expression) -> sympy.Expr:
    """
    Tangent function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Tangent of the input expression.

    Examples
    --------
    >>> tan(0)
    0
    >>> tan(sympy.pi / 4)
    1
    """
    return sympy.tan(expr)


def asin(expr: Expression) -> sympy.Expr:
    """
    Inverse sine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Inverse sine of the input expression.

    Examples
    --------
    >>> asin(0)
    0
    >>> asin(1)
    pi/2
    """
    return sympy.asin(expr)


def acos(expr: Expression) -> sympy.Expr:
    """
    Inverse cosine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Inverse cosine of the input expression.

    Examples
    --------
    >>> acos(1)
    0
    >>> acos(0)
    pi/2
    """
    return sympy.acos(expr)


def atan(expr: Expression) -> sympy.Expr:
    """
    Inverse tangent function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Inverse tangent of the input expression.

    Examples
    --------
    >>> atan(0)
    0
    >>> atan(1)
    pi/4
    """
    return sympy.atan(expr)


def sinh(expr: Expression) -> sympy.Expr:
    """
    Hyperbolic sine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Hyperbolic sine of the input expression.

    Examples
    --------
    >>> sinh(0)
    0
    """
    return sympy.sinh(expr)


def cosh(expr: Expression) -> sympy.Expr:
    """
    Hyperbolic cosine function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Hyperbolic cosine of the input expression.

    Examples
    --------
    >>> cosh(0)
    1
    """
    return sympy.cosh(expr)


def tanh(expr: Expression) -> sympy.Expr:
    """
    Hyperbolic tangent function.

    Parameters
    ----------
    expr : Expression
        Input expression.

    Returns
    -------
    sympy.Expr
        Hyperbolic tangent of the input expression.

    Examples
    --------
    >>> tanh(0)
    0
    """
    return sympy.tanh(expr)


# endregion


# mark all functions as never inline transpile
for func in __all__:
    globals()[func] = never_inline_transpile(globals()[func])
