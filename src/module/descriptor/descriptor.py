from dataclasses import dataclass

from symbols._column import ColVar
from symbols._ode import Compartment
from symbols._omega_eta import Eta
from symbols._sharedvar import SharedVar
from symbols._sigma_eps import Eps
from symbols._theta import Theta


@dataclass(kw_only=True, frozen=True)
class ModuleDescriptor:
    thetas: list[Theta]
    etas: list[Eta]
    epsilons: list[Eps]
    colvars: list[ColVar]
    cmts: list[Compartment]
    sharedvars: list[SharedVar]
    n_cmt: int
    advan: int
    trans: int
    defdose_cmt: int
    defobs_cmt: int

    docstring: str | None = None
