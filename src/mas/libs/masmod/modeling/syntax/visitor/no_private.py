import libcst as cst

from mas.libs.masmod.modeling.syntax.rethrow import rethrow


class NoPrivateVisitor(cst.CSTVisitor):
    """
    A visitor that checks for private attributes in the CST. e.g. __var__.
    It raises a SyntaxError if it finds any private attributes.
    Private attributes are reserved for internal use, and should not be used in user code.
    Use protected attributes (e.g. _var) instead if needed.
    This is to prevent accidental usage of private attributes that are meant for internal implementation details.
    """

    def __init__(self, source_code: str | None = None):
        super().__init__()
        self._source_code = source_code

    def visit_Name(self, node: cst.Name) -> None:
        """
        Visit a Name node in the CST.

        If the name starts with double underscores, it is considered a private variable.
        Raises a NameError if a private variable is found, indicating that it is reserved for internal use.
        """
        if node.value in (
            "__self__",
            "__class__",
            "__init__",
        ):
            # Allow __self__ as it is used in the module descriptor
            return
        if node.value.startswith("__"):
            rethrow(
                NameError(
                    "Private variable is reserved for internal use, use protected variable (e.g. _var) instead if needed."
                ),
                token=node,
                source_code=self._source_code,
            )
