import sympy

from mas.libs.masmod.modeling.typings import Expression

__all__ = [
    "abs",
    "floor",
    "ceiling",
    "sqrt",
    "exp",
    "log",
    "ln",
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


abs = sympy.Abs
floor = sympy.floor
ceiling = sympy.ceiling
exp = sympy.exp
log = sympy.log
ln = log
sin = sympy.sin
cos = sympy.cos
tan = sympy.tan
asin = sympy.asin
acos = sympy.acos
atan = sympy.atan
sinh = sympy.sinh
cosh = sympy.cosh
tanh = sympy.tanh


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


# # mark all functions as never inline transpile
# for func in __all__:
#     globals()[func] = never_inline_transpile(globals()[func])
