import builtins
from typing import NoReturn

import libcst as cst
from libcst._position import CodeRange
from libcst.metadata import PositionProvider

from mtran.unparse import unparse


class MTranError(BaseException):
    def __init__(
        self,
        original_exception: BaseException,
        token: cst.CSTNode,
        source_code: str,
        range: CodeRange | None = None,
    ):
        super().__init__()
        self.token = token
        self.range = range
        self.source_code = source_code
        self.original_exception = original_exception

    def __repr__(self) -> str:
        """Return a string representation of the error."""
        return (
            f"{self.__class__.__name__}({self.token}, {self.range}, "
            f"{self.original_exception})"
        )

    def __str__(self) -> str:
        """Return a string representation of the error."""
        s = f"{self.original_exception.__class__.__name__} raises during MTran"
        if self.range:
            s += f" on row {self.range.start.line}, column {self.range.start.column}:"
        s += "\n"
        if self.range:
            s += indicate_position(self.source_code, self.range)
        else:
            s += self.source_code
        s += "\n"
        s += (
            f"{self.original_exception.__class__.__name__}: {self.original_exception}\n"
        )

        return s


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


def indicate_position(source_code: str, range: CodeRange) -> str:
    """
    Generates a string that visually indicates a specified range within the given source code.
    Args:
        source_code (str): The source code as a single string.
        range (CodeRange): An object representing the start and end positions (with line and column) of the range to indicate.
    Returns:
        str: A string with '^' or '|' characters marking the specified range within the source code.
    Notes:
        - If the range is within a single line, '^' characters are used to highlight the range.
        - If the range spans multiple lines, '^' and '|' characters are used to indicate the start, continuation, and end of the range.
    """

    start = range.start
    end = range.end

    code_lines = source_code.splitlines()

    s = ""
    if start.line == end.line:  # single line, use '^' to indicate position
        # print three lines of code before
        s += "\n".join(code_lines[max(0, start.line - 4) : start.line - 1]) + "\n"
        # print the line with the indicated range
        s += code_lines[start.line - 1] + "\n"
        s += " " * (start.column - 1)
        s += "^" * (end.column - start.column + 1) + "\n"
        # print three lines of code after
        s += (
            "\n".join(code_lines[start.line : min(len(code_lines), end.line + 4)])
            + "\n"
        )

    else:  # multi-line, use '|' to indicate position
        s += " " * (start.column - 1)
        s += "^" * (len(code_lines[start.line - 1]) - start.column + 1)
        s += "\n"
        for i in builtins.range(start.line, end.line - 1):
            s += " " * (len(code_lines[i]) - 1)
            s += "|\n"
        s += " " * (len(code_lines[end.line - 1]) - 1)
        s += "^" * (end.column - 1)
    return s


def rethrow(
    e: BaseException,
    token: cst.CSTNode,
    source_code: str | None = None,
) -> NoReturn:
    # Look up the position of the token in the source code
    visitor = PositionVisitor(token)
    if source_code is None:
        token.visit(visitor)
        source_code = unparse(token)
    else:
        cst.MetadataWrapper(cst.parse_module(source_code)).visit(visitor)
    if visitor.position is not None:
        raise MTranError(
            e,
            token=token,
            source_code=source_code,
            range=visitor.position,
        )
    else:
        # If the position is not found, raise a generic error
        raise MTranError(
            e,
            token=token,
            source_code=source_code,
        )
