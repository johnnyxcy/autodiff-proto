import pathlib
import types
import typing

from utils.inspect_hack import inspect
from utils.loggings import logger


def is_ipynb() -> bool:
    """检查当前运行时是否是 IPython"""
    try:
        # NOTE: 如果运行时是 IPython, 那么 get_ipython 会作为 builtin 函数注册至 globals
        ipy = get_ipython()  # type: ignore

        if ipy is None:
            return False

        shell: str = ipy.__class__.__name__
        logger.debug("Running under IPython with {}".format(shell))

        if shell == "ZMQInteractiveShell":
            return True  # jupyter notebook or qtconsole

        elif shell == "TerminalInteractiveShell":
            return False  # running in IPython

        else:
            return False  # Other
    except ImportError:
        return False  # IPython not found
    except NameError:
        return False  # Normal Python


def find_global_context(mod: object) -> dict[str, typing.Any]:
    _global_context: dict[str, typing.Any] | None = getattr(mod, "_m__globals__", None)

    if _global_context:
        return _global_context

    call_stacks = inspect.stack()
    if is_ipynb():
        import IPython.utils.frame

        for depth in range(len(call_stacks)):
            _mod: types.ModuleType
            ipython_ctx: dict[str, typing.Any]
            _mod, ipython_ctx = IPython.utils.frame.extract_module_locals(depth)
            if "__name__" in ipython_ctx.keys():
                if ipython_ctx["__name__"] == "__main__":
                    _global_context = {**ipython_ctx}
                    break
    else:
        cls_source_file = inspect.getsourcefile(mod.__class__)
        if not cls_source_file:
            raise ValueError("Failed to locate source file for `Module` definition")
        for frame in call_stacks:
            if pathlib.Path(frame.filename) == pathlib.Path(cls_source_file):
                f_globals = frame[0].f_globals
                _global_context = {}
                for f_global_name, f_global_val in f_globals.items():
                    _global_context[f_global_name] = f_global_val
                break

    if _global_context is None:
        logger.warning(
            "Failed to get global context, this might affect Module translation."
        )
        return {}

    return _global_context
