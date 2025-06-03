from typing import Any

import libcst as cst
from sympy import Symbol, latex, parse_expr
from sympy.parsing.sympy_parser import auto_number, auto_symbol, repeated_decimals

from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.syntax.unparse import unparse


class LateXifyVisitor(cst.CSTVisitor):
    """
    A visitor that converts a CST expression to a LaTeX string.
    """

    def __init__(
        self,
        symbols: list[Symbol],
        source_code: str,
        locals: dict[str, Any],
        globals: dict[str, Any],
    ):
        self._symbols = symbols
        self.content: list[str] = []
        self._source_code = source_code
        self._locals = locals
        self._globals = globals

        self._symbol_names: dict[Symbol, str] = {}
        for s in symbols:
            if isinstance(s, Theta):
                self._symbol_names[s] = "\\theta_{" + s.name + "}"
            elif isinstance(s, Eta):
                self._symbol_names[s] = "\\eta_{" + s.name + "}"
            elif isinstance(s, Eps):
                self._symbol_names[s] = "\\epsilon_{" + s.name + "}"
            else:
                self._symbol_names[s] = s.name

    def _unparse(self, node: cst.CSTNode) -> str:
        return unparse(node).strip()

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine):
        body = node.body
        if len(body) != 1:
            self.content.append(self._unparse(node))
            return False

        stmt = body[0]
        if isinstance(stmt, cst.Assign):
            # Handle assignment
            targets = stmt.targets

            if len(targets) != 1:
                self.content.append(self._unparse(node))
                return False

            target = targets[0]

            if isinstance(target.target, cst.Name):
                lhs = target.target.value
                rhs = stmt.value

                try:
                    lhs_symbol = Symbol(lhs)
                    rhs_parsed = parse_expr(
                        self._unparse(rhs),
                        transformations=(
                            auto_number,
                            auto_symbol,
                            repeated_decimals,
                        ),
                        local_dict=self._locals,
                    )

                except Exception as _:
                    self.content.append(self._unparse(node))
                    return False

                # Convert to LaTeX
                lhs_latex = self._latex(lhs_symbol)
                rhs_latex = self._latex(rhs_parsed)
                latex_line = f"{lhs_latex} &= {rhs_latex} \\\\"
                self.content.append(latex_line)
                return

            else:
                # Handle other types of targets (e.g., attribute assignments)
                self.content.append(self._unparse(node))
                return False

    def _latex(self, expr: Any) -> str:
        return latex(expr, symbol_names=self._symbol_names)

    def finalize(self) -> str:
        """
        Finalize the visitor and return the LaTeX string.
        """
        return "\n".join(self.content)
