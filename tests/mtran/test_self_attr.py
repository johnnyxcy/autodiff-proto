import inspect

import libcst as cst

from mtran.transformers.self_attr import SelfAttrMangler
from mtran.unparse import unparse
from symbols._symvar import SymVar


def test_simple_symbols():
    class Simple:
        def __init__(self):
            self.tv = SymVar("tv")
            self.iiv = SymVar("iiv")

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
