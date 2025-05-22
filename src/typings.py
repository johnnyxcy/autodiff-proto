from sympy import Expr

ValueType = int | float
Expression = int | float | Expr
BoundsType = tuple[ValueType | None, ValueType | None]
