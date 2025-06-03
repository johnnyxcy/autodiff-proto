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
from sympy.core.function import FunctionClass

from mas.libs.masmod.modeling.syntax.eval import eval_token
from mas.libs.masmod.modeling.syntax.transformers.inline.flags import (
    InlineTranspileStageLiteralType,
    should_inline_transpile,
)

__all__ = ["InlineFunctionTranspiler"]


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

    def __init__(self, mangler: Mangler):
        super().__init__()
        self._mangler = mangler
        self._names: list[str] = []

    def visit_Name(self, node: cst.Name):
        context = self.get_metadata(ExpressionContextProvider, node, None)
        if context == ExpressionContext.STORE:
            if node.value == "self":
                # Do not rename 'self' variable
                return
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

    If the function has a return value, it will be stored in the `return_` attribute with mangled return variable name.
    """

    to: cst.Call | cst.Name | None
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
        stage: InlineTranspileStageLiteralType,
        source_code: str,
        locals: dict[str, Any],
        globals: dict[str, Any],
    ):
        super().__init__()
        self._stage: InlineTranspileStageLiteralType = stage
        self._source_code = source_code
        self._locals = locals
        self._globals = globals

        self._inline_replace_map: dict[
            tuple[cst.Call, cst.BaseStatement],  # Call node and its parent statement
            InlineFunctionReplacement,  # Replacement for the function call
        ] = {}

        self._func_call_count: dict[
            str, int
        ] = {}  # Track the number of function calls, and use it in mangler to avoid name clashes

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

        if not should_inline_transpile(func_, stage=self._stage):
            # If the function is marked as do not inline, return None
            return None

        if isinstance(func_, FunctionClass):
            # If the function is a SymPy FunctionClass, we can use its name directly
            func_name = func_.__name__
            return InlineFunctionReplacement(
                to=node.with_changes(func=cst.Name(value=func_name)),
                body=[],
            )
        if inspect.isbuiltin(func_):
            # If the function is a built-in function, we cannot inline it
            return None

        try:
            func_src = inspect.getsource(func_).strip()

        except Exception as _:
            # Bypass if we cannot get the source code
            return None
        module = inspect.getmodule(func_)
        _locals = self._locals.copy()
        if module:
            for k, v in inspect.getmembers(module):
                if k.startswith("__") and k.endswith("__"):
                    # Skip dunder methods
                    continue
                _locals[k] = v
        func_def = cst.parse_statement(func_src)
        if not isinstance(func_def, cst.FunctionDef):
            # If the node is not a function definition, return None
            return None

        # If there are nested function calls in function body, inline them first
        nested_transpiler = InlineFunctionTranspiler(
            stage=self._stage,
            source_code=func_src,
            locals=_locals,
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
        count = self._func_call_count.get(func_name, 0)

        def rename_(name: str) -> str:
            # Rename the function arguments to avoid name clashes
            s = f"__{func_name}__{name}"
            if count > 0:
                s += f"__{count}"
            return s

        mangler = LocalVariableMangler(mangler=rename_)
        wrapped = MetadataWrapper(cst.Module(body=[func_def]))
        renamed = wrapped.visit(mangler)
        func_def = cst.ensure_type(
            cst.ensure_type(renamed, cst.Module).body[0],
            cst.FunctionDef,
        )
        self._func_call_count[func_name] = count + 1

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
            if arg.keyword is not None:
                named_arguments[arg.keyword.value] = arg.value
            else:
                named_arguments[params.params[index].name.value] = arg.value
            index += 1

        # If function has default values, fill them in
        for param in params.params:
            if param.default and param.name.value not in named_arguments:
                named_arguments[param.name.value] = param.default

        stmts: list[cst.BaseStatement] = []
        replacement = InlineFunctionReplacement(to=None, body=[])

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
        for index, stmt in enumerate(func_body.body):
            if isinstance(stmt, cst.SimpleStatementLine):
                # special cases
                # is docstring
                if (
                    index == 0
                    and isinstance(stmt.body[0], cst.Expr)
                    and isinstance(stmt.body[0].value, cst.SimpleString)
                ):
                    # If the first statement is a docstring, we skip
                    continue

                # is return statement
                if len(stmt.body) == 1 and isinstance(stmt.body[0], cst.Return):
                    if stmt.body[0].value is not None:
                        ret_name = cst.Name(value=rename_("return"))
                        replacement.to = ret_name
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
                        continue
            # Add the body statement to the list
            stmts.append(stmt)
        replacement.body = stmts
        return replacement

    def _transform_Suite(
        self, original_suite: cst.BaseSuite, updated_suite: cst.BaseSuite
    ) -> cst.BaseSuite:
        """
        Transform a suite of statements by inlining function calls.

        This method is used to transform a suite of statements by inlining function calls
        that have been marked for inlining. It replaces the original function call with the
        inlined nodes.
        """
        new_body: list[cst.BaseStatement] = []
        original_block = cst.ensure_type(original_suite, cst.IndentedBlock)
        updated_block = cst.ensure_type(updated_suite, cst.IndentedBlock)
        if len(original_block.body) != len(updated_block.body):
            # If the original and updated body lengths are different,
            # we cannot inline the function call, so return the updated suite
            return updated_suite
        for idx, stmt in enumerate(original_block.body):
            updated_stmt = cst.ensure_type(updated_block.body[idx], cst.BaseStatement)
            if isinstance(stmt, cst.SimpleStatementLine):
                for (
                    _,
                    stmt_to_replace,
                ), replacement in self._inline_replace_map.items():
                    if stmt_to_replace == stmt:
                        # Replace the statement with the inlined nodes
                        new_body.extend(replacement.body)
                        # We CANNOT break here
                        # because there may be multiple inlined nodes with in the statement
                new_body.append(updated_stmt)
            elif isinstance(stmt, cst.BaseCompoundStatement) and isinstance(
                updated_stmt, cst.BaseCompoundStatement
            ):
                updated_stmt = updated_stmt.with_changes(
                    body=self._transform_Suite(
                        original_suite=stmt.body,
                        updated_suite=updated_stmt.body,
                    ),
                )
                if isinstance(stmt, cst.If) and isinstance(updated_stmt, cst.If):
                    if stmt.orelse is not None and updated_stmt.orelse is not None:
                        updated_stmt = updated_stmt.with_changes(
                            orelse=updated_stmt.orelse.with_changes(
                                body=self._transform_Suite(
                                    original_suite=stmt.orelse.body,
                                    updated_suite=updated_stmt.orelse.body,
                                )
                            )
                        )
                new_body.append(updated_stmt)

        return updated_suite.with_changes(body=new_body)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ):
        return updated_node.with_changes(
            body=self._transform_Suite(
                original_suite=original_node.body,
                updated_suite=updated_node.body,
            )
        )

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
            self._inline_replace_map[(node, parent)] = inlined_nodes

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call):
        # Replace the original Function call if needed
        for (call_node, _), replacement in self._inline_replace_map.items():
            # If the function call is inlined and `to` is specified
            # which means we need to replace the call with the inlined nodes
            if call_node == original_node and replacement.to is not None:
                if isinstance(replacement.to, cst.Call):
                    # replace the call with the replaced Call node
                    return replacement.to
                else:
                    # replace the call with the named return value
                    return cst.Name(value=replacement.to.value)
        # Otherwise, return the updated node
        return updated_node
