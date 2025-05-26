from typing import Generator

from sympy import Basic, Symbol

from symbols._ode import CmtSolvedA, Compartment
from symbols._omega_eta import Eta
from symbols._sigma_eps import Eps
from symbols._theta import Theta


class SymbolDefs(list[Theta | Eta | Eps | Compartment]):
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

    def iter_cmt_A(self) -> Generator[CmtSolvedA, None, None]:
        """Get all compartment A symbols in the definition."""
        for s in self:
            if isinstance(s, Compartment):
                yield s.A

    def iter_symbols(self) -> Generator[Symbol, None, None]:
        """Get all symbols in the definition."""
        for s in self:
            if isinstance(s, Theta):
                yield s
            elif isinstance(s, Eta):
                yield s
            elif isinstance(s, Eps):
                yield s
            elif isinstance(s, Compartment):
                yield s.A
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
            elif isinstance(s, Compartment) and s.A == symbol:
                return True
        return False
