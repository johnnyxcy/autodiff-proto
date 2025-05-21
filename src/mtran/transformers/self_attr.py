import libcst as cst
from libcst.metadata import ExpressionContext, ExpressionContextProvider

from mtran.with_comment import with_comment

MANGLE_PREFIX = "__self__"


def mangle_self_attr(attr_name: str) -> str:
    """
    Mangling function for self attributes.
    """
    return MANGLE_PREFIX + attr_name


def unmangle_self_attr(attr_name: str) -> str:
    """
    Unmangling function for self attributes.
    """
    if attr_name.startswith(MANGLE_PREFIX):
        return attr_name[len(MANGLE_PREFIX) :]
    return attr_name


class SelfAttrMangler(cst.CSTTransformer):
    METADATA_DEPENDENCIES = (ExpressionContextProvider,)

    def __init__(self):
        super().__init__()
        self._mangled: dict[cst.Attribute, cst.Name] = {}

    def leave_Attribute(
        self, original_node: cst.Attribute, updated_node: cst.Attribute
    ):
        context = self.get_metadata(ExpressionContextProvider, original_node, None)
        if context is None:
            return updated_node
        if context == ExpressionContext.LOAD:
            if isinstance(updated_node.attr, cst.Name):
                if (
                    isinstance(updated_node.value, cst.Name)
                    and updated_node.value.value == "self"
                ):
                    # This is a self attribute
                    mangled = cst.Name(value=mangle_self_attr(updated_node.attr.value))
                    self._mangled[updated_node] = mangled
                    return mangled
        return updated_node

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        if not isinstance(updated_node.body, cst.IndentedBlock):
            return updated_node
        new_body: list[cst.BaseStatement] = []
        for attr, mangled_name in self._mangled.items():
            # Replace the attribute with the mangled name
            new_body.append(
                with_comment(
                    cst.SimpleStatementLine(
                        body=[
                            cst.Assign(
                                targets=[cst.AssignTarget(target=mangled_name)],
                                value=attr,
                            )
                        ]
                    ),
                    comment="# mtran: ignore",
                )
            )

        new_body.extend(updated_node.body.body)
        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=new_body)
        )
