from mas.libs.masmod.modeling.module.closed_form_solutions.ev_one_cmt import (
    EvOneCmtLinear,
)
from mas.libs.masmod.modeling.module.defs.closed_form import ClosedFormSolutionModule

builtin_solutions = [
    EvOneCmtLinear.Micro,
    EvOneCmtLinear.Physio,
]


def get_qualname(o: ClosedFormSolutionModule) -> str:
    """
    Get the qualified name of the module class.
    """
    for module in builtin_solutions:
        if isinstance(o, module):
            return module.__qualname__

    return o.__class__.__qualname__


__all__ = ["EvOneCmtLinear", "get_qualname"]
