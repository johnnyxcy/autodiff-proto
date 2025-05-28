from typing import Callable, Literal, TypeVar

__all__ = [
    "InlineTranspileStageLiteralType",
    "when_inline_transpile",
    "never_inline_transpile",
    "should_inline_transpile",
]

InlineTranspileStageLiteralType = Literal["preprocess", "postprocess"]
WhenInlineTranspileLiteralType = (
    Literal["always", "never"] | InlineTranspileStageLiteralType
)
CallableT = TypeVar("CallableT", bound=Callable)


def when_inline_transpile(
    when: WhenInlineTranspileLiteralType,
) -> Callable[[CallableT], CallableT]:
    """
    A decorator to mark a function for inline transpilation.

    This decorator can be used to mark functions that should be inlined
    during the transpilation process. The `when` argument specifies when
    the function should be inlined, e.g., "always", "never"
    """

    def decorator(func: CallableT) -> CallableT:
        setattr(func, "_when_inline_transpile", when)
        return func

    return decorator


def never_inline_transpile(func: CallableT) -> CallableT:
    """
    A decorator to mark a function for inline transpilation.

    This decorator can be used to mark functions that should be inlined
    during the transpilation process. It does not modify the function itself.
    """
    setattr(func, "_when_inline_transpile", "never")
    return func


def should_inline_transpile(
    func: Callable, stage: InlineTranspileStageLiteralType
) -> bool:
    """
    Check if a function is marked for inline transpilation.

    Args:
        func (CallableT): The function to check.

    Returns:
        bool: True if the function is marked for inline transpilation, False otherwise.
    """
    when_ = getattr(func, "_when_inline_transpile", "always")
    if when_ == "always":
        # If the function is not marked, we assume it should be inlined
        return True
    if when_ == "never":
        # If the function is marked as never inline, return False
        return False
    return when_ == stage
