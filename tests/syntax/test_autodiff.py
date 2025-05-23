import inspect

import libcst as cst
import pytest
from sympy import exp

from symbols._symvar import SymVar
from syntax.rethrow import MTranError
from syntax.transformers.autodiff import AutoDiffTransformer
from syntax.unparse import unparse


def _transform(src: str, transformer: AutoDiffTransformer):
    """
    Visit the source code with the given transformer.
    """
    return cst.MetadataWrapper(cst.parse_module(src)).visit(transformer)


def test_name_error():
    src = """def pred(self):
    x = some_value_not_defined
    return x
"""
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={},
        globals={},
    )

    with pytest.raises(MTranError) as excinfo:
        cst.MetadataWrapper(cst.parse_module(src)).visit(transformer)
    assert isinstance(excinfo.value.original_exception, NameError)


def test_simple_symbols():
    class SimpleSymbols:
        def __init__(self):
            self.tv = SymVar("tv")
            self.iiv = SymVar("iiv")

        def pred(self):
            x = self.tv * exp(self.iiv)
            return x

    src = inspect.getsource(SimpleSymbols.pred).strip()
    instance = SimpleSymbols()
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
        symbols=[instance.tv, instance.iiv],
        wrt=[instance.iiv],
    )
    transformed = _transform(src, transformer)
    print(transformed.code)


def test_chained_expr():
    class Chained:
        def __init__(self):
            self.tv_v = SymVar("tv_v")
            self.iiv_cl = SymVar("iiv_cl")
            self.iiv_v = SymVar("iiv_v")

        def pred(self):
            tv_v = self.tv_v
            eta_v = self.iiv_v
            eta_cl = self.iiv_cl

            v = tv_v * exp(eta_v)

            cl = 0.134 * exp(eta_cl)

            k = cl / v
            return k

    src = inspect.getsource(Chained.pred).strip()
    instance = Chained()
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
        symbols=[instance.tv_v, instance.iiv_cl, instance.iiv_v],
        wrt=[instance.iiv_v, instance.iiv_cl],
    )

    transformed = _transform(src, transformer)
    print(transformed.code)


def test_if_else():
    class IfElse:
        def __init__(self):
            self.tv_v = SymVar("tv_v")
            self.iiv_v = SymVar("iiv_v")

        def pred(self):
            if self.tv_v > 0:
                v = self.tv_v * exp(self.iiv_v)
            else:
                v = self.tv_v + self.iiv_v

            return v

    expected = """
def pred(self):
    if self.tv_v > 0:
        v = self.tv_v * exp(self.iiv_v)
        __X__[v, self.iiv_v] = tv_v * exp(iiv_v)  # v wrt iiv_v
    else:
        v = self.tv_v + self.iiv_v
        __X__[v, self.iiv_v] = 1  # v wrt iiv_v

    return v
"""
    src = inspect.getsource(IfElse.pred).strip()
    instance = IfElse()
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
        symbols=[instance.tv_v, instance.iiv_v],
        wrt=[instance.iiv_v],
    )

    transformed = _transform(src, transformer)
    assert unparse(transformed) == expected.strip()


def test_override():
    class Override:
        def __init__(self):
            self.tv_v = SymVar("tv_v")
            self.iiv_v = SymVar("iiv_v")

        def pred(self):
            v = self.tv_v * exp(self.iiv_v)
            if self.tv_v > 0:
                v = self.tv_v + self.iiv_v

            return v

    expected = """
def pred(self):
    v = self.tv_v * exp(self.iiv_v)
    __X__[v, self.iiv_v] = tv_v * exp(iiv_v)  # v wrt iiv_v
    if self.tv_v > 0:
        v = self.tv_v + self.iiv_v
        __X__[v, self.iiv_v] = 1  # v wrt iiv_v

    return v
"""

    src = inspect.getsource(Override.pred).strip()
    instance = Override()
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
        symbols=[instance.tv_v, instance.iiv_v],
        wrt=[
            instance.iiv_v,
        ],
    )

    transformed = _transform(src, transformer)
    assert unparse(transformed) == expected.strip()


def test_carryover():
    class Carryover:
        def __init__(self):
            self.tv_v = SymVar("tv_v")
            self.iiv_v = SymVar("iiv_v")

        def pred(self):
            v = self.tv_v * exp(self.iiv_v)
            z = v
            if v < 0:
                z = -v

            return z

    #     expected = """
    # def pred(self):
    #     v = self.tv_v * exp(self.iiv_v)
    #     __X__[v, self.iiv_v] = tv_v * exp(iiv_v)  # v wrt iiv_v
    #     if v > 0:
    #         v = self.tv_v + self.iiv_v
    #         __X__[v, self.iiv_v] = 1  # v wrt iiv_v
    #     z = v
    #     __X__[z, self.iiv_v] = __X__[v, self.iiv_v]  # z wrt iiv_v
    #     if v < 0:
    #         z = -v
    #         __X__[z, self.iiv_v] = -__X__[v, self.iiv_v]  # z wrt iiv_v

    #     return z
    # """

    src = inspect.getsource(Carryover.pred).strip()
    instance = Carryover()
    transformer = AutoDiffTransformer(
        source_code=src,
        locals={
            "self": instance,
        },
        globals={
            "exp": exp,
        },
        symbols=[instance.tv_v, instance.iiv_v],
        wrt=[
            instance.iiv_v,
        ],
    )

    transformed = _transform(src, transformer)
    print(unparse(transformed))
    # assert unparse(transformed) == expected.strip()
