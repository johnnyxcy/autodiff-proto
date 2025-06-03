import inspect

import libcst as cst
from sympy import Symbol

from mas.libs.masmod.modeling.syntax.transformers.self_attr import SelfAttrMangler
from mas.libs.masmod.modeling.syntax.unparse import unparse


def test_simple_symbols():
    class Simple:
        def __init__(self):
            self.tv = Symbol("tv")
            self.iiv = Symbol("iiv")

        def pred(self):
            x = self.tv + self.iiv
            return x

    src = inspect.getsource(Simple.pred).strip()
    transformer = SelfAttrMangler()

    transformed = cst.MetadataWrapper(cst.parse_module(src)).visit(transformer)
    code = unparse(transformed)

    expected = """
def pred(self):
    __self__tv = self.tv  # mtran: ignore
    __self__iiv = self.iiv  # mtran: ignore
    x = __self__tv + __self__iiv
    return x
"""
    assert code.strip() == expected.strip()
