import textwrap
from typing import Any

import libcst as cst
from libcst._nodes.internal import CodegenState
from libcst.metadata import PositionProvider


class PositionVisitor(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, token: cst.CSTNode):
        super().__init__()
        self.token = token
        self.position = None

    def on_visit(self, node: cst.CSTNode) -> bool:
        """Visit a CST node and capture its position."""
        if self.position is not None:
            return False

        if node.deep_equals(self.token):
            self.position = self.get_metadata(PositionProvider, node, None)
            return False
        return True


def eval_token(
    token: cst.CSTNode,
    locals: dict[str, Any],
    globals: dict[str, Any],
    *,
    source_code: str | None = None,
) -> Any:
    """
    Evaluate a CST token in the context of the given locals and globals.

    Args:
        token (cst.CSTNode): The CST token to evaluate.
        locals (dict[str, Any]): Local variables for evaluation.
        globals (dict[str, Any]): Global variables for evaluation.
        source_code (str | None): The source code string.

    Returns:
        Any: The result of the evaluation.
    """
    state = CodegenState(
        default_indent="",
        default_newline="\n",
    )

    token._codegen(state)
    code = "".join(state.tokens)
    try:
        return eval(code, globals, locals)
    except Exception as e:
        # Look up the position of the token in the source code
        visitor = PositionVisitor(token)
        if source_code is None:
            token.visit(visitor)
            source_code = code
        else:
            cst.MetadataWrapper(cst.parse_module(source_code)).visit(visitor)
        if visitor.position is not None:
            start = visitor.position.start
            end = visitor.position.end

            err = f"[MTran] {e.__class__.__name__}: {str(e)}"

            raise SyntaxError(
                err,
                (
                    "<code>",
                    start.line,
                    start.column,
                    source_code,
                    end.line,
                    end.column,
                ),
            )
        else:
            # If the position is not found, raise a generic error
            raise e
