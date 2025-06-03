import inspect

import libcst as cst
import pytest

from mas.libs.masmod.modeling.syntax.rethrow import MTranError
from mas.libs.masmod.modeling.syntax.transformers.inline.flags import (
    when_inline_transpile,
)
from mas.libs.masmod.modeling.syntax.transformers.inline.transpiler import (
    InlineFunctionTranspiler,
)
from mas.libs.masmod.modeling.syntax.unparse import unparse


def add(a, b=1):
    return a + b


def minus(a, b):
    """Subtracts b from a."""
    return a - b


def linear_model(x, w, b):
    return add(x, w * b)


@when_inline_transpile("postprocess")
def only_on_postprocess(a):
    return a + 1


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
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_no_docstring():
    source_code = """
def demo_func(a, b):
    # This is a comment
    z = minus(a, b + a)
"""

    expected_code = """
def demo_func(a, b):
    __minus__a = a
    __minus__b = b + a
    __minus__return = __minus__a - __minus__b
    # This is a comment
    z = __minus__return
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_stages():
    source_code = """
def demo_func(a, b):
    # This is a comment
    z = add(a, b)
    z_final = only_on_postprocess(z)
"""

    expected_code = """
def demo_func(a, b):
    __add__a = a
    __add__b = b
    __add__return = __add__a + __add__b
    # This is a comment
    z = __add__return
    z_final = only_on_postprocess(z)
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code

    expected_final_code = """
def demo_func(a, b):
    __add__a = a
    __add__b = b
    __add__return = __add__a + __add__b
    # This is a comment
    z = __add__return
    __only_on_postprocess__a = z
    __only_on_postprocess__return = __only_on_postprocess__a + 1
    z_final = __only_on_postprocess__return
"""
    transpiler = InlineFunctionTranspiler(
        "postprocess", updated_code, locals(), globals()
    )
    updated_final_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    print(updated_final_code)
    assert updated_final_code == expected_final_code


def test_assign_return():
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
        "preprocess", source_code, locals(), globals()
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
    __linear_model____add__return = __linear_model____add__a + __linear_model____add__b
    __linear_model__return = __linear_model____add__return
    # This is a comment
    z = __linear_model__return
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
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
        "preprocess", source_code, locals(), globals()
    )
    with pytest.raises(MTranError):
        updated_code = (
            cst.MetadataWrapper(
                cst.parse_module(source_code),
            )
            .visit(transpiler)
            .code
        )


def test_return():
    source_code = """def demo_func(a, b, c):
    return add(a, b) + c
"""
    expected_code = """def demo_func(a, b, c):
    __add__a = a
    __add__b = b
    __add__return = __add__a + __add__b
    return __add__return + c
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_multiple_transpilation():
    source_code = """def demo_func(a, b, c):
    return add(a, b) + add(b, c)
"""

    expected_code = """def demo_func(a, b, c):
    __add__a = a
    __add__b = b
    __add__return = __add__a + __add__b
    __add__a__1 = b
    __add__b__1 = c
    __add__return__1 = __add__a__1 + __add__b__1
    return __add__return + __add__return__1
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_if_else():
    source_code = """def demo_func(a, b, c):
    if a > 0:
        return add(a, b)
    else:
        return add(b, c)
"""

    expected_code = """def demo_func(a, b, c):
    if a > 0:
        __add__a = a
        __add__b = b
        __add__return = __add__a + __add__b
        return __add__return
    else:
        __add__a__1 = b
        __add__b__1 = c
        __add__return__1 = __add__a__1 + __add__b__1
        return __add__return__1
"""

    transpiler = InlineFunctionTranspiler(
        "preprocess", source_code, locals(), globals()
    )
    updated_code = (
        cst.MetadataWrapper(
            cst.parse_module(source_code),
        )
        .visit(transpiler)
        .code
    )
    assert updated_code == expected_code


def test_class_inheritance():
    class Base:
        def add(self, a, b):
            return a + b

    class Derived(Base):
        def demo_func(self, a, b, c):
            if a > 0:
                return self.add(a, b)
            else:
                return self.add(b, c)

    source_code = inspect.getsource(Derived.demo_func).strip()

    expected_code = """def demo_func(self, a, b, c):
    if a > 0:
        __add__a = a
        __add__b = b
        __add__return = __add__a + __add__b
        return __add__return
    else:
        __add__a__1 = b
        __add__b__1 = c
        __add__return__1 = __add__a__1 + __add__b__1
        return __add__return__1"""

    locals_ = {**locals(), "self": Derived()}

    transpiler = InlineFunctionTranspiler("preprocess", source_code, locals_, globals())
    transformed = cst.MetadataWrapper(
        cst.parse_module(source_code),
    ).visit(transpiler)
    assert unparse(transformed) == expected_code
