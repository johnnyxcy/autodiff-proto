from __future__ import annotations

from typing import Any

import libcst as cst

from module.defs.module import Module
from module.defs.ode import OdeModule
from syntax.eval import eval_token
from syntax.rethrow import rethrow


class Staticizer(cst.CSTTransformer):
    """
    A transformer that converts dynamic ModuleDef to static ModuleDef.

    It replace __init__ function body with the redefinitions for all instance attributes.

    For Example:
    ```python
    class A:
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c


    class B(A):
        def __init__(self, a, b, c, d=None):
            super().__init__(a, b, c)
            self.d = d or -1


    B(a=1, b=2, c=3, d=4)
    ```

    will be converted to:
    ```python
    class B:
        def __init__(self):
            self.a = 1
            self.b = 2
            self.c = 3
            self.d = 4
    ```
    """

    def __init__(
        self,
        source_code: str,
        locals: dict[str, Any] | None = None,
        globals: dict[str, Any] | None = None,
    ) -> None:
        self._source_code = source_code
        self._locals = locals or {}
        self._globals = globals or {}

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef):
        if len(updated_node.bases) > 0:
            updated_bases = [*updated_node.bases]
            for idx, base in enumerate(updated_node.bases):
                cls_ = eval_token(
                    base.value,
                    locals=self._locals,
                    globals=self._globals,
                    source_code=self._source_code,
                )
                if issubclass(cls_, OdeModule):
                    updated_bases[idx] = cst.Arg(
                        value=cst.Name(value=OdeModule.__name__)
                    )
                elif issubclass(cls_, Module):
                    updated_bases[idx] = cst.Arg(value=cst.Name(value=Module.__name__))
                else:
                    rethrow(
                        TypeError("Unsupported base class for staticization"),
                        token=base,
                        source_code=self._source_code,
                    )
            return updated_node
        else:
            return updated_node.with_changes(
                bases=[cst.Arg(value=cst.Name(value=Module.__name__))]
            )
