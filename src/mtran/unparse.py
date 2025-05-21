import libcst as cst
from libcst._nodes.internal import CodegenState


def unparse(token: cst.CSTNode) -> str:
    """
    Unparse a CST node to its string representation.

    Args:
        token (cst.CSTNode): The CST node to unparse.

    Returns:
        str: The string representation of the CST node.
    """
    state = CodegenState(
        default_indent=" " * 4,
        default_newline="\n",
    )
    token._codegen(state)
    return "".join(state.tokens)
