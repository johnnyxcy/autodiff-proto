import re
from dataclasses import dataclass, field
from typing import Any

from module.defs.module import Module
from module.defs.ode import OdeModule
from symbols._column import AnyColVar, ColVar, ColVarCollection
from symbols._ode import Compartment
from symbols._omega_eta import Eta
from symbols._sharedvar import SharedVar
from symbols._sigma_eps import Eps
from symbols._theta import Theta
from utils.find_global import find_global_context
from utils.inspect_hack import inspect
from utils.loggings import logger


# Best practice: return a dataclass to hold all interpreted results
@dataclass
class InterpretResult:
    _o: Module

    thetas: list[Theta]
    etas: list[Eta]
    epsilons: list[Eps]
    colvars: list[ColVar]
    colvar_collections: list[ColVarCollection[AnyColVar]]
    cmts: list[Compartment]
    sharedvars: list[SharedVar]
    advan: int
    trans: int
    defdose_cmt: int
    defobs_cmt: int
    locals: dict[str, Any] = field(default_factory=dict)
    globals: dict[str, Any] = field(default_factory=dict)


def interpret(mod: Module, src: str | None = None):
    if src is None:
        src = inspect.getsource(mod.__class__)
    else:
        src = src

    visited: set[str] = set()
    # 重要: 这里必须先用 vars(mod) 获取所有的实例属性, 否则会导致排序错误, dir(mod) 是无序的
    attr_names = [*vars(mod).keys(), *dir(mod)]

    thetas: list[Theta] = []
    etas: list[Eta] = []
    epsilons: list[Eps] = []
    colvars: list[ColVar] = []
    colvar_collections: list[ColVarCollection[AnyColVar]] = []
    cmts: list[Compartment] = []
    sharedvars: list[SharedVar] = []

    for attr_name in attr_names:
        if re.match(r"__(.+)__", attr_name):  # 跳过 dunder 方法
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
        elif isinstance(attr, ColVarCollection):
            colvar_collections.append(attr)
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

    # 检查 column_context 和 column_collection_context 的 col_name 是否有重复
    visited_colnames: set[str] = set()
    for v in colvars:
        if v.col_name in visited_colnames:
            raise ValueError(f"Duplicate `column` definition for '{v.col_name}'")
        visited_colnames.add(v.col_name)

    for v in colvar_collections:
        for _, col in enumerate(v.values()):
            if col.col_name in visited_colnames:
                raise ValueError(f"Duplicate `column` definition for '{col.col_name}'")
            visited_colnames.add(col.col_name)

    globals = find_global_context(mod=mod)

    if issubclass(mod.__class__, OdeModule):
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
    else:
        # 非 Ode Module 的话, 不能定义 compartment
        if len(cmts) > 0:
            raise AssertionError(
                "Your module must be derived from OdeModule if any compartment is defined"
            )
        # TODO: ClosedFormSolutionModule
        advan = 0
        trans = 0
        defdose_cmt = 0
        defobs_cmt = 0

    locals = {
        "self": mod,
        "__self__": mod,
        "__class__": mod.__class__,
    }

    return InterpretResult(
        _o=mod,
        thetas=thetas,
        etas=etas,
        epsilons=epsilons,
        colvars=colvars,
        colvar_collections=colvar_collections,
        cmts=cmts,
        sharedvars=sharedvars,
        globals=globals,
        advan=advan,
        trans=trans,
        defdose_cmt=defdose_cmt,
        defobs_cmt=defobs_cmt,
        locals=locals,
    )
