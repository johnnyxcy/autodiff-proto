from __future__ import annotations

import abc
import builtins
import pathlib
import typing

from sympy import Symbol

from symbols._column import AnyColVar, ColVarCollection
from utils.inspect_hack import inspect

if typing.TYPE_CHECKING:
    from typings import Expression  # noqa: F401


__all__ = ["ModuleMetaclass", "Module", "ModuleT"]

T = typing.TypeVar("T")


class ModuleMetaclass(builtins.type):
    def __call__(cls: typing.Type[T], *args: typing.Any, **kwargs: typing.Any) -> T:
        obj = builtins.type.__call__(cls, *args, **kwargs)
        if hasattr(obj, "__post_init__"):
            obj.__post_init__()
        return obj


class Module(object, metaclass=ModuleMetaclass):
    """Base class for all Masmod modules.

    Examples
    --------
    Build a extravascular one compartment model of plasma concentration using closed form solution:

    >>>    class TestModel(Module):
    >>>        def __init__(self) -> None:
    >>>            super().__init__()
    >>>            self.theta_cl = theta(0.1, bounds=(0, None))
    >>>            self.theta_v = theta(8, bounds=(0, None))
    >>>            self.theta_ka = theta(0.5, bounds=(0, None))
    >>>            self.eta_cl = omega(0.08)
    >>>            self.eta_v = omega(0.5)
    >>>            self.eta_ka = omega(0.5)
    >>>            self.eps_prop = sigma(0.01)
    >>>            self.eps_add = sigma(0.5)
    >>>            self.dose = column("DOSE")
    >>>            self.t = column("TIME")
    >>>
    >>>        def pred(self):
    >>>            cl = self.theta_cl * exp(self.eta_cl)
    >>>            v = self.theta_v * exp(self.eta_v)
    >>>            ka = self.theta_ka * exp(self.eta_ka)
    >>>            k = cl / v
    >>>            ipred = self.dose / v * ka / (ka - k) * (exp(-k * self.t) - exp(-ka * self.t))
    >>>            y = ipred * (1 + self.eps_prop) + self.eps_add
    >>>            return y
    """

    def __init__(self) -> None:
        _m__globals__ = {}
        cls_source_file = inspect.getsourcefile(self.__class__)
        if cls_source_file:
            call_stacks = inspect.stack()
            for frame in call_stacks:
                if pathlib.Path(frame.filename) == pathlib.Path(cls_source_file):
                    f_globals = frame[0].f_globals
                    for f_global_name, f_global_val in f_globals.items():
                        if f_global_name.startswith("__") and f_global_name.endswith(
                            "__"
                        ):
                            # is magic variable
                            continue
                        _m__globals__[f_global_name] = f_global_val
                    break
        setattr(self, "_m__globals__", _m__globals__)

    # Notice we intentionally use type comment instead of type hint here to avoid auto imports
    @abc.abstractmethod
    def pred(self):  # type: () -> Expression
        """Build model from the model parameters to the prediction of dv.

        Examples
        --------
        >>> class TestModel(Module):
        >>>     def __init__(self):
        >>>         ...
        >>>
        >>>     def pred(self):
        >>>         y = expression_of_y
        >>>     return y
        """

    def __post_init__(self) -> None:
        # lets check if "pred" is valid

        cls = self.__class__
        mro_ = cls.mro()[1:]  # index = 0 is cls
        while "pred" not in cls.__dict__:
            cls = mro_.pop(0)
            if cls == Module:
                raise AttributeError("需要指定函数 pred, 请查看文档获取更多信息 TODO:")

        # TODO: check signature
        pred_signature = inspect.signature(cls.__dict__["pred"])
        pred_signature_params = list(pred_signature.parameters.items())

        if len(pred_signature_params) != 1 or pred_signature_params[0][0] != "self":
            raise TypeError("pred 函数必须有且仅有一个 self 入参")

        # 将所有 sympy.Symbol 的名称修复为变量名
        namespace = self.__dict__
        col_var_names = []

        for variable_name, variable_obj in namespace.items():
            if isinstance(variable_obj, AnyColVar):
                variable_obj.name = variable_name
                col_var_names.append(
                    variable_name
                )  # variable_name 不存在重复的，字典的特性决定

        for variable_name, variable_obj in namespace.items():
            if isinstance(variable_obj, Symbol):
                variable_obj.name = variable_name

            # if isinstance(variable_obj, Rng):
            #     variable_obj.name = variable_name

            if isinstance(variable_obj, ColVarCollection):
                variable_obj.name = variable_name

                for _, col_var in enumerate(variable_obj.values()):
                    if isinstance(col_var, AnyColVar):
                        col_var_name = f"{variable_name}__{col_var.col_name}"
                        # _, rename = rename_illegal_column(col_var_name, col_var_names) # TODO: use rename_illegal_column
                        col_var_names.append(col_var_name)
                        col_var.name = col_var_name


ModuleT = typing.TypeVar("ModuleT", bound=Module, default=typing.Any)
