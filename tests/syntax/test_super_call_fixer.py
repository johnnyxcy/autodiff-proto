import libcst as cst

from mas.libs.masmod.modeling.syntax.transformers.super_call_fixer import SuperCallFixer


def test_super_call_fixer():
    # Test case 1: Basic super() call
    source_code = """
class Base:
    def __init__(self):
        pass
class Derived(Base):
    def __init__(self):
        super().__init__()
"""
    expected_code = """
class Base:
    def __init__(self):
        pass
class Derived(Base):
    def __init__(self):
        super(__class__, __self__).__init__()
"""
    super_arg_t = cst.Arg(value=cst.Name("__class__"))
    super_arg_obj = cst.Arg(value=cst.Name("__self__"))
    fixer = SuperCallFixer(super_arg_t, super_arg_obj)
    updated_code = cst.parse_module(source_code).visit(fixer).code
    assert updated_code == expected_code


def test_super_call_fixer_with_explicit_args():
    # Test case 2: super() call with explicit arguments
    source_code = """
class Base:
    def __init__(self):
        pass
class Derived(Base):
    def __init__(self):
        super().__init__()
"""
    expected_code = """
class Base:
    def __init__(self):
        pass
class Derived(Base):
    def __init__(self):
        super(type(self), self).__init__()
"""
    fixer = SuperCallFixer()
    updated_code = cst.parse_module(source_code).visit(fixer).code
    assert updated_code == expected_code
