import libcst as cst

__all__ = ["SuperCallFixer"]


class SuperCallFixer(cst.CSTTransformer):
    """
    A CSTTransformer that rewrites all `super()` calls to include explicit arguments.

    This transformer replaces calls to `super()` with `super(type, obj)` by injecting
    the provided `super_arg_t` and `super_arg_obj` as arguments.

    Args:
        super_arg_t (cst.Arg): The first argument to be inserted into `super()`, typically the class type.
        super_arg_obj (cst.Arg): The second argument to be inserted into `super()`, typically the instance.

    Methods:
        leave_Call(original_node, updated_node):
            Replaces any call to `super()` with `super(super_arg_t, super_arg_obj)`.
    """

    def __init__(
        self, super_arg_t: cst.Arg | None = None, super_arg_obj: cst.Arg | None = None
    ):
        super().__init__()
        if super_arg_obj is None:
            super_arg_obj = cst.Arg(value=cst.Name("self"))

        if super_arg_t is None:
            super_arg_t = cst.Arg(
                value=cst.Call(func=cst.Name("type"), args=[super_arg_obj])
            )
        self._super_arg_t = super_arg_t
        self._super_arg_obj = super_arg_obj

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call):
        if (
            isinstance(updated_node.func, cst.Name)
            and updated_node.func.value == "super"
        ):
            # This is a super() call
            return updated_node.with_changes(
                args=[self._super_arg_t, self._super_arg_obj]
            )

        return updated_node
