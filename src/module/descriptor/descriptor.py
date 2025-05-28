from dataclasses import dataclass, field
from typing import Any

import libcst as cst

from module.defs.ode import odeint
from module.descriptor.common import ModuleClassTypeLiteral, SrcEncapsulation
from symbols._cmt import Compartment
from symbols._column import ColVar
from symbols._omega_eta import Eta, Omega
from symbols._sharedvar import SharedVar
from symbols._sigma_eps import Eps, Sigma
from symbols._theta import Theta
from syntax.with_comment import with_comment
from typings import CodeGen


@dataclass(kw_only=True, frozen=True)
class ModuleDescriptor(CodeGen):
    # metadata from class
    class_name: str
    class_type: ModuleClassTypeLiteral
    docstring: str | None = None
    configuration: dict[str, Any] = field(default_factory=dict)

    # metadata from __init__
    thetas: list[Theta]
    etas: list[Eta]
    epsilons: list[Eps]
    colvars: list[ColVar]
    cmts: list[Compartment]
    sharedvars: list[SharedVar]
    n_cmt: int
    advan: int
    trans: int
    defdose_cmt: int
    defobs_cmt: int

    # pred src
    preprocessed_pred: SrcEncapsulation[cst.FunctionDef]
    postprocessed_pred: SrcEncapsulation[cst.FunctionDef]

    @property
    def is_closed_form_solution(self) -> bool:
        """bool: If the module is a closed form solution."""
        return self.class_type not in ["OdeModule", "Module"]

    def _code_gen(self) -> cst.ClassDef:
        """
        Generate the code for the module descriptor.
        """
        class_def_body: list[cst.BaseStatement] = []
        if self.docstring:
            class_def_body.append(
                cst.SimpleStatementLine(
                    body=[cst.Expr(value=cst.SimpleString(value=self.docstring))]
                )
            )
        __init__body: list[cst.BaseStatement] = []
        # super().__init__()
        super_init_args: list[cst.Arg] = []
        if self.class_type == "OdeModule":
            solver = self.configuration.get("odeint.solver", None)
            if solver is not None:
                solver_args: list[cst.Arg] = []
                if solver == "dverk":
                    default_settings = odeint.DVERK().as_configuration_dict()
                elif solver == "lsoda":
                    default_settings = odeint.LSODA().as_configuration_dict()
                else:
                    default_settings = {}

                for key in default_settings:
                    value = self.configuration.get(key, None)
                    if value != default_settings[key]:
                        keyword = key.split(".")[-1]
                        if isinstance(value, bool):
                            if value is True:
                                arg_value = cst.Name(value="True")
                            else:
                                arg_value = cst.Name(value="False")
                        elif isinstance(value, float):
                            arg_value = cst.Float(value=str(value))
                        elif isinstance(value, int):
                            arg_value = cst.Integer(value=str(value))
                        elif isinstance(value, str):
                            arg_value = cst.SimpleString(value=f'"{value}"')
                        else:
                            raise TypeError(
                                f"Unsupported type for solver argument '{key}': {type(value)}"
                            )
                        solver_args.append(
                            cst.Arg(
                                keyword=cst.Name(value=keyword),
                                value=arg_value,
                            )
                        )
                super_init_args.append(
                    cst.Arg(
                        keyword=cst.Name(value="solver"),
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Name(value="odeint"),
                                attr=cst.Name(value=solver.upper()),
                            ),
                            args=solver_args,
                        ),
                    )
                )
        __init__body.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Expr(
                        value=cst.Call(
                            func=cst.Attribute(
                                value=cst.Call(
                                    func=cst.Name(value="super"),
                                    args=[],
                                ),
                                attr=cst.Name(value="__init__"),
                            ),
                            args=super_init_args,
                        )
                    )
                ]
            )
        )
        # theta(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define typical value thetas",
        )
        for i, theta in enumerate(self.thetas):
            line = cst.SimpleStatementLine(body=[theta._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # omega(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define inter-individual variance (iiv) etas",
        )
        visited_omega: set[Omega] = set()
        for i, eta in enumerate(self.etas):
            if eta.omega not in visited_omega:
                line = cst.SimpleStatementLine(body=[eta.omega._code_gen()])
                if i == 0:
                    line = line.with_changes(
                        leading_lines=[cst.EmptyLine(), leading_comment]
                    )
                __init__body.append(line)
                visited_omega.add(eta.omega)

        # sigma(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define random variance (rv) epsilons",
        )
        visited_sigma: set[Sigma] = set()
        for i, eps in enumerate(self.epsilons):
            if eps.sigma not in visited_sigma:
                line = cst.SimpleStatementLine(body=[eps.sigma._code_gen()])
                if i == 0:
                    line = line.with_changes(
                        leading_lines=[cst.EmptyLine(), leading_comment]
                    )
                __init__body.append(line)
                visited_sigma.add(eps.sigma)

        # column(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define covariates (data columns)",
        )
        for i, colvar in enumerate(self.colvars):
            line = cst.SimpleStatementLine(body=[colvar._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # compartment(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define compartments",
        )
        for i, cmt in enumerate(self.cmts):
            line = cst.SimpleStatementLine(body=[cmt._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # sharedvar(...)
        leading_comment = with_comment(
            cst.EmptyLine(),
            comment="Define arbitrary variables",
        )
        for i, sharedvar in enumerate(self.sharedvars):
            line = cst.SimpleStatementLine(body=[sharedvar._code_gen()])
            if i == 0:
                line = line.with_changes(
                    leading_lines=[cst.EmptyLine(), leading_comment]
                )
            __init__body.append(line)

        # Compose
        class_def_body.append(
            cst.FunctionDef(
                name=cst.Name(value="__init__"),
                params=cst.Parameters(
                    params=[
                        cst.Param(name=cst.Name(value="self")),
                    ]
                ),
                body=cst.IndentedBlock(body=__init__body),
            )
        )

        class_def_body.append(self.preprocessed_pred.cst)

        return cst.ClassDef(
            name=cst.Name(value=self.class_name),
            bases=[cst.Arg(cst.parse_expression(self.class_type))],
            body=cst.IndentedBlock(body=class_def_body),
        )
