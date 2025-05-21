import libcst as cst


def with_comment(
    statement: cst.SimpleStatementLine, comment: str
) -> cst.SimpleStatementLine:
    """
    Add a comment to a line of code.

    Args:
        statement (cst.SimpleStatementLine): The line of code to which the comment will be added.

    Returns:
        cst.SimpleStatementLine: The modified line of code with the comment.
    """
    return statement.with_changes(
        trailing_whitespace=cst.TrailingWhitespace(
            whitespace=cst.SimpleWhitespace("  "),
            comment=cst.Comment(value=comment),
        )
    )
