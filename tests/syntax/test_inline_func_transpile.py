import libcst as cst
import pytest

from syntax.transformers.inline_func_transpile import InlineFunctionTranspiler


def add(a, b=1):
    return a + b


def linear_model(x, w, b):
    return add(x, w * b)


def rosenbrock(x, y):
    a = 1 - x
    b = y - x**2
    return a**2 + 100 * b**2


def test_default_arg():
    # Test case 1: Basic super() call
    source_code = """
def demo_func(a, b):
    # This is a comment
    z = add(a)
"""

    expected_code = """
def demo_func(a, b):
    __add__a = a
    __add__b = 1
    __add__return = __add__a + __add__b
    # This is a comment
    z = __add__return
"""

    transpiler = InlineFunctionTranspiler(
        source_code, locals(), globals(), inline_return=True
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_assign_return():
    # Test case 1: Basic super() call
    source_code = """
def demo_func(a, b):
    # This is a comment
    z = add(a, b)
"""

    expected_code = """
def demo_func(a, b):
    __add__a = a
    __add__b = b
    __add__return = __add__a + __add__b
    # This is a comment
    z = __add__return
"""

    transpiler = InlineFunctionTranspiler(
        source_code, locals(), globals(), inline_return=True
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_nested():
    source_code = """
def demo_func(a, b):
    # This is a comment
    z = linear_model(a, b, 0.1)
"""

    expected_code = """
def demo_func(a, b):
    __linear_model__x = a
    __linear_model__w = b
    __linear_model__b = 0.1
    __linear_model____add__a = __linear_model__x
    __linear_model____add__b = __linear_model__w * __linear_model__b
    __linear_model__return = __linear_model____add__a + __linear_model____add__b
    # This is a comment
    z = __linear_model__return
"""

    transpiler = InlineFunctionTranspiler(
        source_code, locals(), globals(), inline_return=True
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_invalid_function():
    source_code = """def demo_func(a, b):
    # This is a comment
    some_function_not_found(a, b)
"""

    transpiler = InlineFunctionTranspiler(
        source_code, locals(), globals(), inline_return=True
    )
    with pytest.raises(NameError):
        updated_code = (
            cst.MetadataWrapper(
                cst.parse_module(source_code),
            )
            .visit(transpiler)
            .code
        )
