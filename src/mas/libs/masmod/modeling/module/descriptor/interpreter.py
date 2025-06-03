import importlib

import libcst as cst

from mas.libs.masmod.modeling.module.defs.module import Module
from mas.libs.masmod.modeling.syntax.unparse import unparse


def interpret_cls_def(cls_def: cst.ClassDef) -> Module:
    """
    Interpret a class definition and return a Module instance.
    """
    class_name = cls_def.name.value
    apis = importlib.import_module("mas.libs.masmod.modeling.api")
    globals_ = {**vars(apis)}
    locals_ = {}
    exec(unparse(cls_def).strip(), globals_, locals_)
    module = locals_[class_name]()
    if not isinstance(module, Module):
        raise TypeError(f"Expected a Module instance, got {type(module)}")
    return module
