import typing

import numpy as np
import numpy.typing as npt


def block_diagonal(
    left: npt.NDArray[typing.Any],
    right: npt.NDArray[typing.Any],
    fill: typing.Any = 0.0,
    dtype: npt.DTypeLike | None = None,
) -> npt.NDArray[typing.Any]:
    """
    Creates a block diagonal matrix from two input arrays.

    Parameters:
        left (npt.NDArray[typing.Any]): The array to be placed in the top-left block.
        right (npt.NDArray[typing.Any]): The array to be placed in the bottom-right block.
        fill (typing.Any, optional): The value to fill in the off-diagonal blocks. Defaults to 0.0.
        dtype (npt.DTypeLike | None, optional): The desired data-type for the output array. If None, the dtype is inferred.

    Returns:
        npt.NDArray[typing.Any]: A new array with `left` and `right` as diagonal blocks and `fill` elsewhere.

    Example:
        >>> a = np.array([[1, 2], [3, 4]])
        >>> b = np.array([[5]])
        >>> block_diagonal(a, b)
        array([[1., 2., 0.],
               [3., 4., 0.],
               [0., 0., 5.]])
    """
    new_array = np.full(
        [left.shape[0] + right.shape[0], left.shape[1] + right.shape[1]], fill, dtype
    )
    new_array[: left.shape[0], : left.shape[1]] = left
    new_array[-right.shape[0] :, -right.shape[1] :] = right
    return new_array
