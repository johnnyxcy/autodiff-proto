from typing import TypeVar

import libcst as cst

CommentableStatementT = TypeVar(
    "CommentableStatementT", bound=cst.SimpleStatementLine | cst.EmptyLine
)


def with_comment(
    statement: CommentableStatementT, comment: str
) -> CommentableStatementT:
    """
    Add a comment to a line of code.

    Args:
        statement (CommentableStatementT): The line of code to which the comment will be added.

    Returns:
        CommentableStatementT: The modified line of code with the comment.
    """
    if not comment.startswith("#"):
        comment = f"# {comment}"
    if isinstance(statement, cst.SimpleStatementLine):
        # If the statement is a SimpleStatementLine, we can add a trailing comment
        return statement.with_changes(
            trailing_whitespace=cst.TrailingWhitespace(
                whitespace=cst.SimpleWhitespace("  "),
                comment=cst.Comment(value=comment),
            )
        )

    if isinstance(statement, cst.EmptyLine):
        # If the statement is an EmptyLine, we can add a comment directly
        # as it does not have any content
        return statement.with_changes(
            comment=cst.Comment(value=comment),
        )

    raise TypeError(
        f"Expected a SimpleStatementLine or EmptyLine, got {type(statement).__name__}"
    )
