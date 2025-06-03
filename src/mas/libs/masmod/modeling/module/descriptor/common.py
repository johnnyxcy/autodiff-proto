from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar, cast

import libcst as cst

from mas.libs.masmod.modeling.syntax.unparse import unparse

ModuleClassTypeLiteral = Literal["OdeModule", "Module"] | str

CompoundStatementT = TypeVar("CompoundStatementT", bound=cst.BaseCompoundStatement)


@dataclass
class SrcEncapsulation(Generic[CompoundStatementT]):
    src: str
    cst: CompoundStatementT

    @classmethod
    def from_src(cls, src: str) -> SrcEncapsulation[CompoundStatementT]:
        """
        Create a SrcEncapsulation from source code and CST.
        """
        return cls(
            src=src,
            cst=cast(
                CompoundStatementT,
                cst.ensure_type(
                    cst.parse_statement(src),
                    cst.BaseCompoundStatement,
                ),
            ),
        )

    def apply_transform(
        self,
        transformer: cst.CSTTransformer,
    ) -> SrcEncapsulation[CompoundStatementT]:
        transformed = cst.MetadataWrapper(cst.Module(body=[self.cst])).visit(
            transformer
        )
        src = unparse(transformed)
        return SrcEncapsulation(
            src=src,
            cst=cst.ensure_type(transformed.body[0], type(self.cst)),
        )
