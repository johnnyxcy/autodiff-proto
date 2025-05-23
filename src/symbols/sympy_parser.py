import libcst as cst
from sympy import (
    Add,
    Basic,
    Derivative,
    Eq,
    Float,
    Gt,
    Integer,
    Le,
    Lt,
    Mul,
    Ne,
    Pow,
    Rational,
    Symbol,
    exp,
)
from sympy.core.relational import Relational

from typings import AsCST


def parse_sympy_expr(expr: Basic | int | float) -> cst.BaseExpression:
    """
    Parse a sympy expression into a CST expression.

    Args:
        expr (Expr): The sympy expression to parse.

    Returns:
        cst.BaseExpression: The parsed CST expression.
    """
    if isinstance(expr, int | Integer):
        if expr < 0:
            return cst.UnaryOperation(
                operator=cst.Minus(),
                expression=cst.Integer(value=str(-expr)),
            )
        return cst.Integer(value=str(expr))

    if isinstance(expr, float | Float):
        if expr < 0:
            return cst.UnaryOperation(
                operator=cst.Minus(),
                expression=cst.Float(value=str(-expr)),
            )
        return cst.Float(value=str(expr))

    if isinstance(expr, Symbol):
        # We have many symbols that needed to be handled
        if isinstance(expr, AsCST):
            # This is a special case, we need to handle it
            return cst.ensure_type(expr.as_cst(), cst.BaseExpression)
        return cst.Name(value=expr.name)

    if isinstance(expr, Add):
        translated = None
        for token in expr.as_ordered_terms():
            assert isinstance(token, Basic)
            if translated is None:
                translated = parse_sympy_expr(token)
            else:
                translated = cst.BinaryOperation(
                    left=translated,
                    operator=cst.Add(),
                    right=parse_sympy_expr(token),
                )
        if translated is None:
            return cst.Integer(value="0")
        else:
            return translated

    if isinstance(expr, Mul):
        translated = None
        for token in expr.as_ordered_factors():
            assert isinstance(token, Basic)
            if translated is None:
                translated = parse_sympy_expr(token)
            else:
                translated = cst.BinaryOperation(
                    left=translated,
                    operator=cst.Multiply(),
                    right=parse_sympy_expr(token),
                )
        if translated is None:
            return cst.Integer(value="0")
        else:
            return translated

    if isinstance(expr, Pow):
        base = parse_sympy_expr(expr.base)
        exp_ = parse_sympy_expr(expr.exp)
        return cst.BinaryOperation(
            left=base,
            operator=cst.Power(),
            right=exp_,
        )

    if isinstance(expr, Rational):
        return cst.BinaryOperation(
            left=parse_sympy_expr(expr.numerator),
            operator=cst.Divide(),
            right=parse_sympy_expr(expr.denominator),
        )

    if isinstance(expr, Relational):
        if isinstance(expr, Eq):
            op = cst.Equal()
        elif isinstance(expr, Ne):
            op = cst.NotEqual()
        elif isinstance(expr, Lt):
            op = cst.LessThan()
        elif isinstance(expr, Le):
            op = cst.LessThanEqual()
        elif isinstance(expr, Gt):
            op = cst.GreaterThan()
        else:
            op = cst.GreaterThanEqual()

        return cst.Comparison(
            left=parse_sympy_expr(expr.lhs),
            comparisons=[
                cst.ComparisonTarget(
                    operator=op,
                    comparator=parse_sympy_expr(expr.rhs),
                )
            ],
        )

    if isinstance(expr, exp):
        exp_ = expr.exp
        return cst.Call(
            func=cst.Name("exp"),
            args=[cst.Arg(value=parse_sympy_expr(exp_))],
        )

    if isinstance(expr, Derivative):
        on_ = expr.expr
        wrt = expr.variables

        if isinstance(on_, Symbol):
            on_name = on_.name
            if len(wrt) != 1:
                raise NotImplementedError(
                    "Only single variable differentiation is supported"
                )
            from symbols._x import XWrt

            return XWrt(on_name, wrt[0]).as_cst()

    raise NotImplementedError(f"Unknown expression type: {type(expr)}")
