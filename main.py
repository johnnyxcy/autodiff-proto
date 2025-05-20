import sys

sys.path.append("src")

from mtran.inline_func_transpile import InlineFunctionTranspiler

source_code = """def demo_func(a, b):
    # This is a comment
    some_function_not_found(a, b)
"""

transpiler = InlineFunctionTranspiler(
    source_code, locals(), globals(), inline_return=True
)
import libcst

libcst.MetadataWrapper(libcst.parse_module(source_code)).visit(transpiler)
