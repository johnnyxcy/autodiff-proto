from dataclasses import dataclass

from symbols._symvar import SymVar


@dataclass
class XWrt:
    x_name: str

    wrt: SymVar
    wrt2nd: SymVar | None

    def __hash__(self):
        return hash((self.x_name, self.wrt, self.wrt2nd))
