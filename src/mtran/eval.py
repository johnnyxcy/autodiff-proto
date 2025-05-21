from typing import Any

import libcst as cst

from mtran.rethrow import rethrow
from mtran.unparse import unparse


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
    try:
        return eval(unparse(token), globals, locals)
    except Exception as e:
        rethrow(
            e,
            token,
            source_code=source_code,
        )
