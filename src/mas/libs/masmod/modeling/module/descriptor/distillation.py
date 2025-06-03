from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import libcst as cst

from mas.libs.masmod.modeling.module.closed_form_solutions import get_qualname
from mas.libs.masmod.modeling.module.defs.closed_form import (
    ClosedFormSolutionModule,
    get_annotated_meta,
)
from mas.libs.masmod.modeling.module.defs.module import Module
from mas.libs.masmod.modeling.module.defs.ode import OdeModule, get_solver
from mas.libs.masmod.modeling.module.descriptor.common import SrcEncapsulation
from mas.libs.masmod.modeling.module.descriptor.descriptor import ModuleDescriptor
from mas.libs.masmod.modeling.symbols._cmt import Compartment
from mas.libs.masmod.modeling.symbols._column import ColVar
from mas.libs.masmod.modeling.symbols._ns import SymbolNamespace
from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._sharedvar import SharedVar
from mas.libs.masmod.modeling.symbols._sigma_eps import Eps
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.symbols._y import likelihood, prediction
from mas.libs.masmod.modeling.syntax.transformers.autodiff import AutoDiffTransformer
from mas.libs.masmod.modeling.syntax.transformers.inline.transpiler import (
    InlineFunctionTranspiler,
)
from mas.libs.masmod.modeling.syntax.transformers.super_call_fixer import SuperCallFixer
from mas.libs.masmod.modeling.syntax.unparse import unparse
from mas.libs.masmod.modeling.syntax.visitor.no_private import NoPrivateVisitor
from mas.libs.masmod.modeling.utils.find_global import find_global_context
from mas.libs.masmod.modeling.utils.inspect_hack import inspect
from mas.libs.masmod.modeling.utils.loggings import logger


@dataclass(kw_only=True, frozen=True)
class RuntimeModuleDescriptor(ModuleDescriptor):
    _o: Module

    locals: dict[str, Any] = field(default_factory=dict)
    globals: dict[str, Any] = field(default_factory=dict)


def distill(mod: Module, src: str | None = None) -> RuntimeModuleDescriptor:
    logger.debug(
        "[MTran::interpret] Start interpreting module: %s", mod.__class__.__name__
    )

    if src is None:
        src = inspect.getsource(mod.__class__)
    else:
        src = src
    logger.debug("[MTran::interpret] Raw source code:\n %s", src.strip())

    parsed_code_module = cst.parse_module(src.strip())
    if len(parsed_code_module.body) != 1:
        raise ValueError(
            "The module source code should contain and only contain class definition, "
            "no other code should be included."
        )
    module_cls_def = SrcEncapsulation(
        src=src, cst=cst.ensure_type(parsed_code_module.body[0], cst.ClassDef)
    )
    docstring = module_cls_def.cst.get_docstring()

    pred_func_def: SrcEncapsulation[cst.FunctionDef] | None = None
    try:
        pred_func_src = inspect.getsource(mod.pred)
        pred_func_def = SrcEncapsulation(
            src=pred_func_src,
            cst=cst.ensure_type(
                cst.parse_module(pred_func_src).body[0], cst.FunctionDef
            ),
        )
    except Exception as _:
        # If inspect fails, try to find the pred function in the module class definition
        for stmt in module_cls_def.cst.body.body:
            if isinstance(stmt, cst.FunctionDef) and stmt.name.value == "pred":
                pred_func_def = SrcEncapsulation(src=unparse(stmt).strip(), cst=stmt)
                break
    if pred_func_def is None:
        raise ValueError(
            "Failed to locate the `pred` function in the module. "
            "Please ensure that the `pred` function is defined in the module."
        )
    visited: set[str] = set()
    # Important: must use vars(mod) to get all instance attributes first, otherwise it will cause sorting errors, dir(mod) is unordered
    attr_names = [*vars(mod).keys(), *dir(mod)]

    thetas: list[Theta] = []
    etas: list[Eta] = []
    epsilons: list[Eps] = []
    colvars: list[ColVar] = []
    # colvar_collections: list[ColVarCollection[AnyColVar]] = []
    cmts: list[Compartment] = []
    sharedvars: list[SharedVar] = []

    for attr_name in attr_names:
        if re.match(r"__(.+)__", attr_name):  # skip dunder methods and attributes
            continue
        attr = getattr(mod, attr_name)
        if attr_name in visited:
            continue
        if isinstance(attr, Theta):
            thetas.append(attr)
        elif isinstance(attr, Eta):
            etas.append(attr)
        elif isinstance(attr, Eps):
            epsilons.append(attr)
        elif isinstance(attr, ColVar):
            colvars.append(attr)
        # elif isinstance(attr, ColVarCollection):
        #     colvar_collections.append(attr)
        elif isinstance(attr, Compartment):
            cmts.append(attr)
        # elif isinstance(attr, Rng):
        #     rng_context[attr_name] = attr
        elif isinstance(attr, int | float | str | bool):  # constant
            sharedvars.append(SharedVar(name=attr_name, init_value=attr))
        # elif isinstance(attr, ClosedFormSolutionCmt):
        #     cfs_cmt_context[attr_name] = attr
        # elif isinstance(attr, types.MethodType | typing.Callable):
        #     func_context[attr_name] = attr

        visited.add(attr_name)
    logger.debug("[MTran::interpret] Attributes found: %s", visited)

    # Check for duplicate column names
    visited_colnames: set[str] = set()
    for v in colvars:
        if v.col_name in visited_colnames:
            raise ValueError(f"Duplicate `column` definition for '{v.col_name}'")
        visited_colnames.add(v.col_name)

    # for v in colvar_collections:
    #     for _, col in enumerate(v.values()):
    #         if col.col_name in visited_colnames:
    #             raise ValueError(f"Duplicate `column` definition for '{col.col_name}'")
    #         visited_colnames.add(col.col_name)

    globals = find_global_context(o=mod)

    if isinstance(mod, OdeModule):
        n_cmt = len(cmts)
        default_dose: int | None = None
        default_obs: int | None = None
        central_index: int | None = None
        depot_index: int | None = None
        for i, cmt in enumerate(cmts):
            name = cmt.name
            index = i + 1  # index start with 1
            if cmt.default_dose:
                if default_dose is not None:
                    raise ValueError("default_dose can only be set to one compartment")
                default_dose = index
            if cmt.default_obs:
                if default_obs is not None:
                    raise ValueError("default_obs can only be set to one compartment")
                default_obs = index

            if re.match(r".*central.*", name.lower()):
                if central_index is not None:
                    logger.warning(
                        "Multiple compartments are named with pattern 'central'"
                    )
                    central_index = None
                else:
                    central_index = index

            if re.match(r".*(depot|dose|dosing).*", name.lower()):
                if depot_index is not None:
                    logger.warning(
                        "Multiple compartments are named with pattern 'depot | dose | dosing'"
                    )
                    depot_index = None
                else:
                    depot_index = index
        if default_dose is None:
            if depot_index is None:
                logger.warning("No dosing compartment")
                depot_index = 0
            default_dose = depot_index
        if default_obs is None:
            if central_index is None:
                logger.warning("No observation compartment")
                central_index = 0
            default_obs = central_index

        defdose_cmt = default_dose
        defobs_cmt = default_obs
        advan = 0
        trans = 0
        class_type = OdeModule.__name__
        configuration = get_solver(mod).as_configuration_dict()
    else:
        configuration = {}
        # If the module is not derived from OdeModule, no compartments can be defined.
        if len(cmts) > 0:
            raise AssertionError(
                "Your module must be derived from OdeModule if any compartment is defined"
            )

        if isinstance(mod, ClosedFormSolutionModule):
            metadata = get_annotated_meta(mod.__class__)
            advan = metadata.advan
            trans = metadata.trans
            defdose_cmt = metadata.defdose_cmt
            defobs_cmt = metadata.defobs_cmt
            n_cmt = metadata.n_cmt
            class_type = get_qualname(mod)
        else:
            advan = 0
            trans = 0
            defdose_cmt = 0
            defobs_cmt = 0
            n_cmt = 0
            class_type = Module.__name__

    locals = {
        "self": mod,
        "__self__": mod,
        "__class__": mod.__class__,
        "prediction": prediction,
        "likelihood": likelihood,
    }
    # Check 1: No Private Variables
    visitor = NoPrivateVisitor(source_code=src)
    cst.parse_module(src).visit(visitor)

    # region: Preprocess pred function
    logger.debug("[MTran::distill] Preprocess transforms")
    # Transform 1: Fix super()
    logger.debug("[MTran::distill] super() call fixer@preprocess")
    fixer = SuperCallFixer()
    preprocessed_pred_func_def = pred_func_def.apply_transform(fixer)

    # Transform 2: Inline Function Transpile
    logger.debug("[MTran::distill] Inline function transpile@preprocess")
    transpiler = InlineFunctionTranspiler(
        stage="preprocess",
        source_code=preprocessed_pred_func_def.src,
        locals=locals,
        globals=globals,
    )
    preprocessed_pred_func_def = preprocessed_pred_func_def.apply_transform(transpiler)
    logger.debug(
        "[MTran::distill] Preprocessed finished\n%s",
        preprocessed_pred_func_def.src,
    )
    # endregion

    # TODO: should save CST here before autodiff

    # region: Postprocess pred function
    # Transform 1: Inline Function Transpile for finalization
    logger.debug("[MTran::distill] Inline function transpile@postprocess")
    transpiler = InlineFunctionTranspiler(
        stage="postprocess",
        source_code=preprocessed_pred_func_def.src,
        locals=locals,
        globals=globals,
    )
    postprocessed_pred_func_def = preprocessed_pred_func_def.apply_transform(transpiler)

    # Transform 2: Automatic Gradient
    logger.debug("[MTran::distill] Automatic differentiation@postprocess")
    autodiff_transformer = AutoDiffTransformer(
        source_code=postprocessed_pred_func_def.src,
        locals=locals,
        globals=globals,
        symbol_defs=SymbolNamespace([*thetas, *etas, *epsilons, *cmts, *colvars]),
        module_cls=mod.__class__,
    )
    postprocessed_pred_func_def = postprocessed_pred_func_def.apply_transform(
        autodiff_transformer
    )
    logger.debug(
        "[MTran::distill] Postprocess finished\n%s",
        postprocessed_pred_func_def.src,
    )
    # endregion

    return RuntimeModuleDescriptor(
        _o=mod,
        class_name=mod.__class__.__name__,
        class_type=class_type,
        configuration=configuration,
        preprocessed_pred=preprocessed_pred_func_def,
        postprocessed_pred=postprocessed_pred_func_def,
        thetas=thetas,
        etas=etas,
        epsilons=epsilons,
        colvars=colvars,
        # colvar_collections=colvar_collections,
        cmts=cmts,
        sharedvars=sharedvars,
        globals=globals,
        n_cmt=n_cmt,
        advan=advan,
        trans=trans,
        defdose_cmt=defdose_cmt,
        defobs_cmt=defobs_cmt,
        locals=locals,
        docstring=docstring,
    )
