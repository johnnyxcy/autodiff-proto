import inspect

import libcst as cst
from sympy import exp

from symbols._omega_eta import Eta
from symbols._theta import Theta
from syntax.visitor.latexify import LateXifyVisitor


def test_simple():
    class Simple:
        def __init__(self):
            self.tv_v = Theta("tv_v")
            self.iiv_cl = Eta("iiv_cl")
            self.iiv_v = Eta("iiv_v")

        def pred(self):
            tv_v = self.tv_v
            eta_v = self.iiv_v
            eta_cl = self.iiv_cl

            v = tv_v * exp(eta_v)

            cl = 0.134 * exp(eta_cl)

            k = cl / v
            return k

    src = inspect.getsource(Simple.pred).strip()
    instance = Simple()
    visitor = LateXifyVisitor(
        symbols=[instance.tv_v, instance.iiv_cl, instance.iiv_v],
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
    )
    cst.parse_module(src).visit(visitor)

    print(visitor.finalize())
