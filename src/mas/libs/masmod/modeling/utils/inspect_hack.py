import inspect
import sys
import typing

__all__ = ["inspect"]


# some hacky implementation to locate file within ipython kernel
def new_getfile(obj: typing.Any) -> str:
    """重新处理 inspect.getfile 的逻辑

    当 inspect.getfile(obj) obj 为 Class 的时候，首先会尝试是否有 __file__
    属性，如果没有则通过 Class 中任意函数定位对应的文件位置
    """
    if inspect.ismodule(obj):
        if getattr(obj, "__file__", None):
            return obj.__file__  # type: ignore
        raise TypeError("{!r} is a built-in module".format(obj))

    # region modifications
    if inspect.isclass(obj):
        if hasattr(obj, "__module__"):
            module = sys.modules.get(obj.__module__)
            if getattr(module, "__file__", None):
                return module.__file__  # type: ignore
        for _, member in inspect.getmembers(obj):
            if (
                inspect.isfunction(member)
                and member.__qualname__ == f"{obj.__qualname__}.{member.__name__}"
            ):
                return inspect.getfile(member)
        raise TypeError("Source code for {!r} is not available".format(obj))
    # endregion

    if inspect.ismethod(obj):
        obj = obj.__func__
    if inspect.isfunction(obj):
        obj = obj.__code__
    if inspect.istraceback(obj):
        obj = obj.tb_frame
    if inspect.isframe(obj):
        obj = obj.f_code
    if inspect.iscode(obj):
        return obj.co_filename
    raise TypeError(
        "module, class, method, function, traceback, frame, or code object was expected, got {}".format(
            type(object).__name__
        )
    )


inspect.getfile = new_getfile
