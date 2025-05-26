import inspect

import libcst as cst
import pytest
from sympy import exp

from symbols._omega_eta import Eta
from symbols._theta import Theta
from syntax.rethrow import MTranError
from syntax.visitor.no_private import NoPrivateVisitor


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

            __v = tv_v * exp(eta_v)

            cl = 0.134 * exp(eta_cl)

            k = cl / __v
            return k

    src = inspect.getsource(Simple.pred).strip()
    visitor = NoPrivateVisitor(source_code=src)
    with pytest.raises(
        MTranError, match="Private variable is reserved for internal use"
    ):
        cst.parse_module(src).visit(visitor)
