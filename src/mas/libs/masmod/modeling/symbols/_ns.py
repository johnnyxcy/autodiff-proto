from typing import Generator

from sympy import Basic, Symbol

from mas.libs.masmod.modeling.symbols._cmt import Compartment
from mas.libs.masmod.modeling.symbols._column import ColVar
from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps
from mas.libs.masmod.modeling.symbols._theta import Theta


class SymbolNamespace(list[Theta | Eta | Eps | Compartment | ColVar]):
    def iter_theta(self) -> Generator[Theta, None, None]:
        """Get all theta symbols in the definition."""
        for s in self:
            if isinstance(s, Theta):
                yield s

    def iter_eta(self) -> Generator[Eta, None, None]:
        """Get all eta symbols in the definition."""
        for s in self:
            if isinstance(s, Eta):
                yield s

    def iter_eps(self) -> Generator[Eps, None, None]:
        """Get all epsilon symbols in the definition."""
        for s in self:
            if isinstance(s, Eps):
                yield s

    def iter_cmt(self) -> Generator[Compartment, None, None]:
        """Get all compartments in the definition."""
        for s in self:
            if isinstance(s, Compartment):
                yield s

    def iter_colvar(self) -> Generator[ColVar, None, None]:
        """Get all column variables in the definition."""
        for s in self:
            if isinstance(s, ColVar):
                yield s

    def iter_symbols(self) -> Generator[Symbol, None, None]:
        """Get all symbols in the definition."""
        for s in self:
            if isinstance(s, Theta):
                yield s
            elif isinstance(s, Eta):
                yield s
            elif isinstance(s, Eps):
                yield s
            elif isinstance(s, ColVar):
                yield s
            else:
                raise TypeError(f"Unknown symbol type: {type(s)}")

    def has_symbol(self, symbol: Basic) -> bool:
        """Check if the symbol is in the definition."""
        for s in self:
            if isinstance(s, Theta) and s == symbol:
                return True
            elif isinstance(s, Eta) and s == symbol:
                return True
            elif isinstance(s, Eps) and s == symbol:
                return True
            elif isinstance(s, ColVar) and s == symbol:
                return True

        return False
