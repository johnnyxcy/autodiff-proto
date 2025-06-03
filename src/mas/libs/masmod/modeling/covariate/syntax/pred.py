import libcst as cst
import polars as pl

from mas.libs.masmod.modeling.covariate.spec import (
    AnyCovariatesInclusion,
    CategoricalCovariateInclusion,
    ContinuousCovariateInclusion,
)
from mas.libs.masmod.modeling.syntax.with_comment import with_comment


def _build_categorical_pred_lines(
    param_name: cst.Name, inclusion: CategoricalCovariateInclusion, data: pl.DataFrame
):
    lvls = data[inclusion.covariate.col_name].unique()
    dtype = inclusion.covariate.dtype
    tv_name = inclusion.on.name
    cov_name = inclusion.covariate.name
    _state = inclusion.state
    lines: list[cst.BaseStatement] = [
        cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=param_name)],
                    value=cst.Integer(value="1"),
                )
            ]
        )
    ]
    if _state == "linear":
        lines[0] = with_comment(
            lines[0],
            comment=f"# Categorical {cov_name} on {tv_name}",
        )
        for idx, lvl in enumerate(lvls):
            cat_lvl = lvl if dtype == "numeric" else str(lvl)
            if dtype == "numeric":
                if isinstance(cat_lvl, float):
                    # If the level is a float, we use a Float node
                    comparator = cst.Float(value=str(cat_lvl))
                elif isinstance(cat_lvl, int):
                    comparator = cst.Integer(value=str(cat_lvl))
                else:
                    # We cannot decide, use a SimpleString
                    comparator = cst.SimpleString(value=f'"{cat_lvl}"')
            else:
                comparator = cst.SimpleString(value=f'"{cat_lvl}"')
            if idx == 0:
                body = cst.IndentedBlock(
                    body=[
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[cst.AssignTarget(target=param_name)],
                                    value=cst.Integer(value="1"),
                                )
                            ]
                        )
                    ],
                )
            else:
                value = cst.parse_expression(f"self.{param_name.value}_{idx} + 1")
                body = cst.IndentedBlock(
                    body=[
                        cst.SimpleStatementLine(
                            body=[
                                cst.Assign(
                                    targets=[cst.AssignTarget(target=param_name)],
                                    value=value,
                                )
                            ]
                        )
                    ],
                )

            lines.append(
                cst.If(
                    test=cst.Comparison(
                        left=cst.Attribute(
                            value=cst.Name(value="self"), attr=cst.Name(cov_name)
                        ),
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=comparator,
                            )
                        ],
                    ),
                    body=body,
                )
            )
    return lines


def _build_continuous_pred_lines(
    param_name: cst.Name, inclusion: ContinuousCovariateInclusion, data: pl.DataFrame
):
    lines: list[cst.BaseStatement] = []
    median = data[inclusion.covariate.col_name].median()
    tv_name = inclusion.on.name
    cov_name = inclusion.covariate.name
    _state = inclusion.state

    if _state == "exclude":
        lines.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=param_name)],
                        value=cst.Integer(value="1"),
                    )
                ]
            )
        )
    elif _state == "linear":
        lines.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=param_name)],
                        value=cst.parse_expression(
                            f"1 + self.{param_name.value}_1 * (self.{cov_name} - {median})"
                        ),
                    )
                ],
                leading_lines=[
                    cst.EmptyLine(
                        comment=cst.Comment(value=f"# Linear {cov_name} on {tv_name}")
                    )
                ],
            )
        )
    elif _state == "exp":
        lines.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=param_name)],
                        value=cst.parse_expression(
                            f"exp(self.{param_name.value}_1 * (self.{cov_name} - {median}))"
                        ),
                    )
                ],
                leading_lines=[
                    cst.EmptyLine(
                        comment=cst.Comment(
                            value=f"# Exponential {cov_name} on {tv_name}"
                        )
                    )
                ],
            )
        )
    elif _state == "power":
        lines.append(
            cst.SimpleStatementLine(
                body=[
                    cst.Assign(
                        targets=[cst.AssignTarget(target=param_name)],
                        value=cst.parse_expression(
                            f"(self.{cov_name} / {median}) ** self.{param_name.value}_1"
                        ),
                    )
                ],
                leading_lines=[
                    cst.EmptyLine(
                        comment=cst.Comment(value=f"# Power {cov_name} on {tv_name}")
                    )
                ],
            )
        )

    elif _state == "piecewise":
        declaration = cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=param_name)],
                    value=cst.Integer(value="1"),
                )
            ],
            leading_lines=[
                cst.EmptyLine(
                    comment=cst.Comment(value=f"# Piecewise {cov_name} on {tv_name}")
                )
            ],
        )

        piecewise_le_median_assignment = cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=param_name)],
                    value=cst.parse_expression(
                        f"1 + self.{param_name.value}_1 * (self.{cov_name} - {median})"
                    ),
                )
            ]
        )

        piecewise_gt_median_assignment = cst.SimpleStatementLine(
            body=[
                cst.Assign(
                    targets=[cst.AssignTarget(target=param_name)],
                    value=cst.parse_expression(
                        f"1 + self.{param_name.value}_2 * (self.{cov_name} - {median})"
                    ),
                )
            ],
        )

        lines.extend(
            [
                declaration,
                cst.If(
                    test=cst.parse_expression(f"self.{cov_name} <= {median}"),
                    body=cst.IndentedBlock(body=[piecewise_le_median_assignment]),
                ),
                cst.If(
                    test=cst.parse_expression(f"self.{cov_name} > {median}"),
                    body=cst.IndentedBlock(body=[piecewise_gt_median_assignment]),
                ),
            ]
        )
    else:
        raise NotImplementedError("Unsupported _s=%s" % _state)
    return lines


def include_covariate_in_pred(
    param_name: cst.Name, inclusion: AnyCovariatesInclusion, data: pl.DataFrame
):
    if isinstance(inclusion, CategoricalCovariateInclusion):
        return _build_categorical_pred_lines(param_name, inclusion, data)
    elif isinstance(inclusion, ContinuousCovariateInclusion):
        return _build_continuous_pred_lines(param_name, inclusion, data)
    else:
        raise ValueError(f"Unsupported case type {type(inclusion)}")
