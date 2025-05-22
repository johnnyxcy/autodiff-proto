import inspect
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

import libcst as cst
from libcst.metadata import (
    ExpressionContext,
    ExpressionContextProvider,
    MetadataWrapper,
    ParentNodeProvider,
    ScopeProvider,
)

from syntax.eval import eval_token


class Mangler(Protocol):
    def __call__(self, name: str) -> str:
        """Rename a variable name."""
        ...


class LocalVariableMangler(cst.CSTTransformer):
    """
    A CSTTransformer that renames local variable names in a Python syntax tree.

    This transformer uses metadata providers to identify variable names in store context
    (i.e., when variables are being assigned) and applies a renaming function to them.
    It ensures that each variable is only renamed once by tracking names that have already
    been processed.

    Attributes:
        METADATA_DEPENDENCIES (tuple): Required metadata providers for parent node, scope, and expression context.
        _mangler (Mangler): A callable that takes a variable name and returns its new name.
        _names (list[str]): List of variable names that have already been renamed.

    Methods:
        visit_Name(node):
            Records variable names in store context to avoid renaming them multiple times.
        leave_Name(original_node, updated_node):
            Renames variable names in store context using the provided Mangler function.
    """

    METADATA_DEPENDENCIES = (
        ParentNodeProvider,
        ScopeProvider,
        ExpressionContextProvider,
    )

    def __init__(self, Mangler: Mangler):
        super().__init__()
        self._mangler = Mangler
        self._names: list[str] = []

    def visit_Name(self, node: cst.Name):
        context = self.get_metadata(ExpressionContextProvider, node)
        if context == ExpressionContext.STORE:
            if node.value not in self._names:
                # If the variable is not already renamed, add it to the list
                # to avoid renaming it again
                self._names.append(node.value)

    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        # Rename the variable name if is store
        name = updated_node.value
        if name in self._names:
            new_name = self._mangler(updated_node.value)
            if new_name != name:
                return updated_node.with_changes(value=new_name)
        return updated_node


@dataclass
class InlineFunctionReplacement:
    """
    A class to represent the replacement of a function call with its body.
    """

    return_: cst.Name | None
    body: Sequence[cst.BaseStatement]


class InlineFunctionTranspiler(cst.CSTTransformer):
    """
    A CSTTransformer that inlines function calls by replacing them with the function's body.

    This transformer analyzes function calls within the code, retrieves the source and body of the called function,
    and replaces the call with the corresponding statements from the function body. It handles renaming of local
    variables to avoid name clashes, supports inlining of nested function calls, and can optionally inline return
    values as assignments.

    Attributes:
        METADATA_DEPENDENCIES (tuple): Metadata providers required for this transformer.

        source_code (str): The source code being transformed.
        locals (dict[str, Any]): Local variables available for function resolution.
        globals (dict[str, Any]): Global variables available for function resolution.
        inline_return (bool, optional): Whether to inline return values as assignments. Defaults to False.

    Methods:
        _transpile_inline_call(node: cst.Call) -> InlineFunctionReplacement | None:
            Inlines a function call by replacing it with the function's body, handling argument mapping and variable renaming.

        leave_FunctionDef(original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
            Replaces function calls within a function definition with their inlined bodies.

        visit_Call(node: cst.Call):
            Detects function calls that can be inlined and stores their replacements for later transformation.
    """

    METADATA_DEPENDENCIES = (ParentNodeProvider,)

    def __init__(
        self,
        source_code: str,
        locals: dict[str, Any],
        globals: dict[str, Any],
        inline_return: bool = False,
    ):
        super().__init__()
        self._source_code = source_code
        self._locals = locals
        self._globals = globals
        self._inline_return = inline_return

        self._inline_replace_map: dict[cst.CSTNode, InlineFunctionReplacement] = {}

    def _transpile_inline_call(
        self, node: cst.Call
    ) -> InlineFunctionReplacement | None:
        """
        Inline the function call by replacing it with the function's body.

        This method looks up the function being called and retrieves its body,
        then replaces the call node with the body.

        Args:
            node (cst.Call): The call node to be inlined.
        Returns:
            list[cst.BaseStatement]: A list of CST nodes representing the inlined function body.
        """
        func_ = eval_token(
            node.func,
            self._locals,
            self._globals,
            source_code=self._source_code,
        )
        try:
            func_src = inspect.getsource(func_)
        except OSError:
            # Bypass if we cannot get the source code
            return None

        func_def = cst.ensure_type(cst.parse_statement(func_src), cst.FunctionDef)

        # If there are nested function calls in function body, inline them first
        nested_transpiler = InlineFunctionTranspiler(
            source_code=func_src,
            locals=self._locals,
            globals=self._globals,
        )
        transpiled = MetadataWrapper(cst.Module(body=[func_def])).visit(
            nested_transpiler
        )
        func_def = cst.ensure_type(
            cst.ensure_type(transpiled, cst.Module).body[0],
            cst.FunctionDef,
        )
        func_name = func_def.name.value

        def rename_(name: str) -> str:
            # Rename the function arguments to avoid name clashes
            return f"__{func_name}__{name}"

        Mangler = LocalVariableMangler(Mangler=rename_)
        wrapped = MetadataWrapper(cst.Module(body=[func_def]))
        renamed = wrapped.visit(Mangler)
        func_def = cst.ensure_type(
            cst.ensure_type(renamed, cst.Module).body[0],
            cst.FunctionDef,
        )

        # Collect the arguments passed to the function call
        # and create a mapping of argument names to their values
        # Skip the first argument if it's 'self'
        params = func_def.params

        # Create a mapping of argument names to their values
        named_arguments: dict[str, cst.BaseExpression] = {}
        index = 0
        for arg in node.args:
            if index == 0 and params.params[0].name.value == "self":
                # Skip the first argument if it's 'self'
                index += 1
                continue
            if arg.keyword is not None:
                named_arguments[arg.keyword.value] = arg.value
            else:
                named_arguments[params.params[index].name.value] = arg.value
            index += 1

        # If function has default values, fill them in
        for param in params.params:
            if param.default and param.name.value not in named_arguments:
                named_arguments[param.name.value] = param.default

        replacement = InlineFunctionReplacement(return_=None, body=[])
        stmts: list[cst.BaseStatement] = []

        # Put renamed arguments into the function body
        for name, value in named_arguments.items():
            stmts.append(
                cst.SimpleStatementLine(
                    body=[
                        cst.Assign(
                            targets=[
                                cst.AssignTarget(cst.Name(value=name)),
                            ],
                            value=value,
                        )
                    ],
                ),
            )
        func_body = cst.ensure_type(func_def.body, cst.IndentedBlock)
        for stmt in func_body.body:
            if (
                isinstance(stmt, cst.SimpleStatementLine)
                and len(stmt.body) == 1
                and isinstance(stmt.body[0], cst.Return)
            ):
                # Replace the return statement with the inlined value
                if stmt.body[0].value is not None:
                    if self._inline_return:
                        ret_name = cst.Name(value=rename_("return"))
                        replacement.return_ = ret_name
                        stmts.append(
                            stmt.with_changes(
                                body=[
                                    cst.Assign(
                                        targets=[
                                            cst.AssignTarget(ret_name),
                                        ],
                                        value=stmt.body[0].value,
                                    )
                                ]
                            )
                        )
                    else:  # normal return
                        stmts.append(stmt)
            else:
                # Add the body statement to the list
                stmts.append(stmt)
        replacement.body = stmts
        return replacement

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        body: list[cst.BaseStatement] = []
        func_body = cst.ensure_type(original_node.body, cst.IndentedBlock)
        for stmt in func_body.body:
            if self._inline_replace_map.get(stmt) is not None:
                # Replace the function call with the inlined nodes
                inlined_nodes = self._inline_replace_map[stmt]
                body.extend(inlined_nodes.body)

                # If the inlined nodes contain a return statement, and the return value is received by a variable
                if (
                    inlined_nodes.return_ is not None
                    and isinstance(stmt, cst.SimpleStatementLine)
                    and len(stmt.body) == 1
                    and isinstance(stmt.body[0], (cst.Assign, cst.AugAssign))
                ):
                    body.append(
                        stmt.with_changes(
                            body=[
                                stmt.body[0].with_changes(value=inlined_nodes.return_)
                            ]
                        )
                    )

            else:
                # Keep the original statement if it's not a function call
                body.append(stmt)
        return updated_node.with_changes(body=func_body.with_changes(body=body))

    def visit_Call(self, node: cst.Call):
        parent = self.get_metadata(ParentNodeProvider, node, None)
        while parent is not None:
            if isinstance(parent, cst.BaseStatement):
                # If the parent node is a statement, we can inline the call
                break
            parent = self.get_metadata(ParentNodeProvider, parent, None)
        if parent is None:
            # If the parent node is not a statement, we cannot inline the call
            return
        # Inline the function call
        inlined_nodes = self._transpile_inline_call(node)
        if inlined_nodes is not None:
            # Store the mapping of the original call node to the inlined nodes
            self._inline_replace_map[parent] = inlined_nodes
