from __future__ import annotations

import typing
from _collections_abc import dict_items, dict_keys, dict_values

import libcst as cst
from sympy import Symbol
from typing_extensions import Self

from typings import CodeGen

ColumnDtypeLiteral = typing.Literal["numeric", "str"]
ColumnDtypeTypeAlias = typing.Type[int | float | str]
ColumnDtype = ColumnDtypeLiteral | ColumnDtypeTypeAlias


def is_numeric_dtype(dtype: ColumnDtype) -> bool:
    return dtype == "numeric" or dtype in [int, float]


class ColVar(Symbol, CodeGen):
    """Column variable."""

    __slots__ = ("_col_name",)

    def __new__(cls, name: str, col_name: str, **kwargs: typing.Any):
        instance = super().__new__(cls, name, **kwargs)  # type: ignore
        instance._col_name = col_name
        return instance

    def __deepcopy__(self, memo: typing.Any) -> Self:
        ins = type(self)(name=self.name, col_name=self.col_name)
        # 此处更名是因为 Symbol 重新复制并不会生成新的对象，而是用原始对象，
        # 原始对象如果更名了就导致拷贝后的对象和原始对象 name 不一致
        ins.name = self.name
        return ins

    @property
    def col_name(self) -> str:
        return self._col_name

    @property
    def dtype(self) -> ColumnDtypeLiteral:
        """ColumnDtype: Data type in the column."""
        ...

    @property
    def is_categorical(self) -> bool:
        """bool: Whether the data in this column is categorical."""
        ...

    def is_same_as(self, other: ColVar) -> bool:
        return (
            type(self) is type(other)
            and self.name == other.name
            and self.col_name == other.col_name
            and self.dtype == other.dtype
            and self.is_categorical == other.is_categorical
        )

    def as_pretty_str(self) -> str:
        return f"{type(self).__qualname__}(name={self.name}, col_name={self.col_name}, dtype={self.dtype}, is_categorical={self.is_categorical})"

    def _code_gen(self):
        args: list[cst.Arg] = [cst.Arg(cst.Name(value=self.col_name))]
        if self.dtype != "numeric":
            args.append(
                cst.Arg(
                    keyword=cst.Name(value="dtype"),
                    value=cst.SimpleString(value="categorical"),
                )
            )

        if self.is_categorical:
            args.append(
                cst.Arg(
                    keyword=cst.Name(value="is_categorical"),
                    value=cst.Name(value="True"),
                )
            )

        return cst.Assign(
            targets=[cst.AssignTarget(cst.Name(value=self.name))],
            value=cst.Call(func=cst.Name(value=column.__name__), args=args),
        )


T = typing.TypeVar("T", covariant=True, bound=ColVar)


class ColVarCollection(typing.Generic[T]):
    def __init__(
        self,
        name: str,
        dtype: ColumnDtypeLiteral,
        is_categorical: bool,
        collection: list[T],
    ) -> None:
        super().__init__()
        self.name = name
        self.dtype = dtype
        self.is_categorical = is_categorical
        self._m: dict[str, T] = {col_var.col_name: col_var for col_var in collection}

    def __contains__(self, key: str) -> bool:
        return key in self._m.keys()

    def __getitem__(self, key: str) -> T:
        return self._m[key]

    def items(self) -> dict_items[str, T]:
        return self._m.items()

    def keys(self) -> dict_keys[str, T]:
        return self._m.keys()

    def values(self) -> dict_values[str, T]:
        return self._m.values()


NumericColVarT = typing.TypeVar("NumericColVarT", bound="NumericColVar")


class NumericColVar(ColVar):
    @property
    def dtype(self) -> typing.Literal["numeric"]:
        return "numeric"


class NumericContinuousColVar(NumericColVar):
    """Variable represents a column that contains numeric continuous data."""

    @property
    def is_categorical(self) -> typing.Literal[False]:
        return False


class NumericCategoricalColVar(NumericColVar):
    """Variable represents a column that contains numeric categorical data."""

    @property
    def is_categorical(self) -> typing.Literal[True]:
        return True


StrCategoricalColVarT = typing.TypeVar(
    "StrCategoricalColVarT", bound="StrCategoricalColVar"
)


class StrColVar(ColVar):
    @property
    def dtype(self) -> typing.Literal["str"]:
        return "str"


class StrCategoricalColVar(StrColVar):
    """Variable represents a column that contains string data."""

    @property
    def is_categorical(self) -> typing.Literal[True]:
        return True


NumericCategoricalColVarCollection = ColVarCollection[NumericCategoricalColVar]
NumericContinuousColVarCollection = ColVarCollection[NumericContinuousColVar]
StrCategoricalColVarCollection = ColVarCollection[StrCategoricalColVar]
AnyColVarCollection = (
    NumericCategoricalColVarCollection
    | NumericContinuousColVarCollection
    | StrCategoricalColVarCollection
)
AnyCategoricalColVar = NumericCategoricalColVar | StrCategoricalColVar
AnyContinuousColVar = NumericContinuousColVar
AnyColVar = AnyCategoricalColVar | AnyContinuousColVar


@typing.overload
def column(
    col_name: str,
    dtype: typing.Literal["numeric"] | typing.Type[int | float] = "numeric",
    *,
    is_categorical: typing.Literal[False] = False,
) -> NumericContinuousColVar:
    """Create a variable to represent a column containing numeric continuous data.

    Parameters
    ----------
    col_name : str
        Name of column to be represented.
    dtype : Literal["numeric"], optional
        Type of data in the column. Defaults to `"numeric"`.
    is_categorical : Literal[False], optional
        Whether the data in this column is categorical. Defaults to `False`.

    Returns
    -------
    NumericContinuousColVar
        A variable represents the column.

    Examples
    --------
    Create a variable represents the "WEIGHT" column:

    >>>    class TestModel(Module):
    >>>        def __init__(self) -> None:
    >>>            super().__init__()
    >>>            ...
    >>>            self.wt = column("WEIGHT")
    """
    ...


@typing.overload
def column(
    col_name: str,
    dtype: typing.Literal["numeric"] | typing.Type[int | float] = "numeric",
    *,
    is_categorical: typing.Literal[True],
) -> NumericCategoricalColVar:
    """Create a variable to represent a column containing numeric categorical data.

    Parameters
    ----------
    col_name : str
        Name of column to be represented.
    dtype : Literal["numeric"], optional
        Type of data in the column. Defaults to `"numeric"`.
    is_categorical : Literal[True], optional
        Whether the data in this column is categorical. Defaults to `True`.

    Returns
    -------
    NumericCategoricalColVar
        A variable represents the column.

    Examples
    --------
    Create a variable represents the "DOSE" column:

    >>>    class TestModel(Module):
    >>>        def __init__(self) -> None:
    >>>            super().__init__()
    >>>            ...
    >>>            self.dose = column("DOSE", is_categorical=True)
    """
    ...


@typing.overload
def column(
    col_name: str,
    dtype: typing.Literal["str"] | typing.Type[str],
    *,
    is_categorical: typing.Literal[True] = True,
) -> StrCategoricalColVar:
    """Create a variable to represent a column containing string data.

    Parameters
    ----------
    col_name : str
        Name of column to be represented.
    dtype : Literal["str"], optional
        Type of data in the column. Defaults to `"str"`.

    Returns
    -------
    StrCategoricalColVar
        A variable represents the column.

    Examples
    --------
    Create a variable represents the "SEX" column:

    >>>    class TestModel(Module):
    >>>        def __init__(self) -> None:
    >>>            super().__init__()
    >>>            ...
    >>>            self.sex = column("SEX", dtype="str")
    """
    ...


def column(
    col_name: str, dtype: ColumnDtype = "numeric", *, is_categorical: bool = False
) -> NumericContinuousColVar | NumericCategoricalColVar | StrCategoricalColVar:
    return _column_impl(
        col_name=col_name,
        dtype=dtype,
        is_categorical=is_categorical,
    )


def _column_impl(
    col_name: str, dtype: ColumnDtype = "numeric", *, is_categorical: bool = False
) -> NumericContinuousColVar | NumericCategoricalColVar | StrCategoricalColVar:
    if is_numeric_dtype(dtype):
        if is_categorical:
            return NumericCategoricalColVar(name=col_name, col_name=col_name)
        else:
            return NumericContinuousColVar(name=col_name, col_name=col_name)
    else:
        return StrCategoricalColVar(name=col_name, col_name=col_name)


# @typing.overload
# def multicolumn(
#     col_name: list[str],
#     dtype: typing.Literal["numeric"] = "numeric",
#     *,
#     is_categorical: typing.Literal[False] = False,
# ) -> NumericContinuousColVarCollection:
#     """Create a variable to represent a list of columns containing numeric continuous data.

#     Parameters
#     ----------
#     col_name : list[str]
#         A list of column names for the columns to be represented.
#     dtype : Literal["numeric"], optional
#         Type of data in the columns. Defaults to `"numeric"`.
#     is_categorical : Literal[False], optional
#         Whether the data in the columns are categorical. Defaults to `False`.

#     Returns
#     -------
#     NumericContinuousColVarCollection
#         A variable represents multiple columns.

#     Examples
#     --------
#     Create a variable represents the "WEIGHT" and "AGE" column:

#     >>>    class TestModel(Module):
#     >>>        def __init__(self) -> None:
#     >>>            super().__init__()
#     >>>            ...
#     >>>            self.con_cov = multicolumn(["WEIGHT", "AGE"])
#     """
#     ...


# @typing.overload
# def multicolumn(
#     col_name: list[str],
#     dtype: typing.Literal["numeric"] = "numeric",
#     *,
#     is_categorical: typing.Literal[True],
# ) -> NumericCategoricalColVarCollection:
#     """Create a variable to represent a list of columns containing numeric categorical data.

#     Parameters
#     ----------
#     col_name : list[str]
#         A list of column names for the columns to be represented.
#     dtype : Literal["numeric"], optional
#         Type of data in the columns. Defaults to `"numeric"`.
#     is_categorical : Literal[True], optional
#         Whether the data in the columns are categorical. Defaults to `True`.

#     Returns
#     -------
#     NumericCategoricalColVarCollection
#         A variable represents multiple columns.

#     Examples
#     --------
#     Create a variable represents the "GROUP" and "DOSE" column:

#     >>>    class TestModel(Module):
#     >>>        def __init__(self) -> None:
#     >>>            super().__init__()
#     >>>            ...
#     >>>            self.cat_cov = multicolumn(["GROUP", "DOSE"], is_categorical=True)
#     """
#     ...


# @typing.overload
# def multicolumn(
#     col_name: list[str],
#     dtype: typing.Literal["str"],
#     *,
#     is_categorical: typing.Literal[True] = True,
# ) -> StrCategoricalColVarCollection:
#     """Create a variable to represent a list of columns containing string data.

#     Parameters
#     ----------
#     col_name : list[str]
#         A list of column names for the columns to be represented.
#     dtype : Literal["str"], optional
#         Type of data in the columns. Defaults to `"str"`.

#     Returns
#     -------
#     StrCategoricalColVarCollection
#         A variable represents multiple columns.

#     Examples
#     --------
#     Create a variable represents the "SEX" and "NAME" column:

#     >>>    class TestModel(Module):
#     >>>        def __init__(self) -> None:
#     >>>            super().__init__()
#     >>>            ...
#     >>>            self.str_cov = multicolumn(["SEX", "NAME"], dtype="str")
#     """
#     ...


# def multicolumn(
#     col_name: list[str],
#     dtype: ColumnDtypeLiteral = "numeric",
#     *,
#     is_categorical: bool = False,
# ) -> (
#     NumericContinuousColVarCollection
#     | NumericCategoricalColVarCollection
#     | StrCategoricalColVarCollection
# ):
#     return ColVarCollection(  # pyright: ignore[reportReturnType]
#         name="_unnamed_multicolumn",
#         dtype=dtype,
#         is_categorical=is_categorical,
#         collection=[
#             _column_impl(col_name=_col_name, dtype=dtype, is_categorical=is_categorical)
#             for _col_name in col_name
#         ],
#     )
