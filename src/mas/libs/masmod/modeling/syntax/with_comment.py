from typing import TypeVar

import libcst as cst

CommentableStatementT = TypeVar(
    "CommentableStatementT",
    bound=cst.BaseStatement | cst.EmptyLine,
)

TrailingCommentableStatementT = TypeVar(
    "TrailingCommentableStatementT",
    bound=cst.BaseStatement,
)


def with_trailing_comment(
    statement: TrailingCommentableStatementT, comment: str
) -> TrailingCommentableStatementT:
    """
    Add a trailing comment to a line of code.

    Args:
        statement (cst.BaseStatement): The line of code to which the comment will be added.
        comment (str): The comment to be added.

    Returns:
        cst.BaseStatement: The modified line of code with the comment.
    """
    if not comment.startswith("#"):
        comment = f"# {comment}"
    return statement.with_changes(
        trailing_whitespace=cst.TrailingWhitespace(
            whitespace=cst.SimpleWhitespace("  "),
            comment=cst.Comment(value=comment),
        )
    )


def with_comment(
    statement: CommentableStatementT, comment: str
) -> CommentableStatementT:
    """
    Add a comment to a line of code.

    Args:
        statement (CommentableStatementT): The line of code to which the comment will be added.
        comment (str): The comment to be added.

    Returns:
        CommentableStatementT: The modified line of code with the comment.
    """
    if not comment.startswith("#"):
        comment = f"# {comment}"
    if isinstance(statement, cst.SimpleStatementLine | cst.BaseCompoundStatement):
        # If the statement is a SimpleStatementLine or a BaseCompoundStatement, we put the comment
        # as a leading line.
        return statement.with_changes(
            leading_lines=[
                cst.EmptyLine(comment=cst.Comment(value=comment)),
                *statement.leading_lines,
            ]
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
