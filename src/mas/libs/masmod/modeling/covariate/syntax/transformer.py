import libcst as cst
import polars as pl
from libcst.metadata import ExpressionContext, ExpressionContextProvider

from mas.libs.masmod.modeling.covariate.naming import make_parcov_varname
from mas.libs.masmod.modeling.covariate.spec import AnyCovariatesInclusion
from mas.libs.masmod.modeling.covariate.syntax.init import include_covariate_in_init
from mas.libs.masmod.modeling.covariate.syntax.pred import include_covariate_in_pred
from mas.libs.masmod.modeling.syntax.with_comment import (
    with_comment,
)


class CovariateInclusionTransformer(cst.CSTTransformer):
    """
    A transformer that includes covariates in the model.
    This transformer modifies the model to include covariates as needed.
    """

    METADATA_DEPENDENCIES = (ExpressionContextProvider,)

    def __init__(
        self,
        inclusions: list[AnyCovariatesInclusion],
        data: pl.DataFrame,
    ) -> None:
        self._data = data

        self._init_lines: list[cst.BaseStatement] = []
        self._pred_lines: list[cst.BaseStatement] = []

        # theta: [cov_name, ...]
        self._included_relations: dict[str, list[str]] = {}

        for inclusion in inclusions:
            varname = make_parcov_varname(
                covariate_name=inclusion.covariate.name, on_param_name=inclusion.on.name
            )
            param_name = cst.Name(value=varname)
            init_lines = include_covariate_in_init(
                param_name=param_name,
                inclusion=inclusion,
                data=self._data,
            )
            self._init_lines.extend(init_lines)
            pred_lines = include_covariate_in_pred(
                param_name=param_name,
                inclusion=inclusion,
                data=self._data,
            )
            self._pred_lines.extend(pred_lines)
            theta_name = inclusion.on.name
            self._included_relations[theta_name] = self._included_relations.get(
                theta_name, []
            ) + [param_name.value]

    def leave_Attribute(self, original_node, updated_node):
        context = self.get_metadata(ExpressionContextProvider, original_node, None)
        # If the attribute is 'self' and we are in a LOAD context,
        # we do mangle it with '{name}__with_cov'.
        if (
            context == ExpressionContext.LOAD
            and isinstance(updated_node.value, cst.Name)
            and updated_node.value.value == "self"
            and updated_node.attr.value in self._included_relations.keys()
        ):
            new_name = f"{updated_node.attr.value}__with_cov"
            return cst.Name(value=new_name)
        return updated_node

    def leave_FunctionDef(self, original_node, updated_node):
        if updated_node.name.value == "__init__":
            return self._leave_FunctionDef_init(original_node, updated_node)

        if updated_node.name.value == "pred":
            return self._leave_FunctionDef_pred(original_node, updated_node)

        return updated_node

    def _leave_FunctionDef_init(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        current_body = updated_node.body
        if not isinstance(current_body, cst.IndentedBlock):
            return updated_node
        new_body = [
            *current_body.body,
            *self._init_lines,
        ]
        return updated_node.with_changes(body=cst.IndentedBlock(body=new_body))

    def _leave_FunctionDef_pred(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """
        This method is called when leaving the 'pred' function definition.
        It includes covariates in the prediction function based on the inclusions.
        """
        current_body = updated_node.body
        if not isinstance(current_body, cst.IndentedBlock):
            return updated_node

        new_body = [*self._pred_lines]
        for theta_name, param_names in self._included_relations.items():
            # Create a new variable for the theta with covariates
            rhs: str = f"self.{theta_name}"
            for param_name in param_names:
                rhs = f"{rhs} * {param_name}"
            if rhs:
                theta_with_cov_assignment = with_comment(
                    cst.parse_statement(f"{theta_name}__with_cov = {rhs}"),
                    comment=f"# {theta_name} with covariates",
                )
                new_body.append(theta_with_cov_assignment)

        new_body.extend(current_body.body)

        return updated_node.with_changes(body=cst.IndentedBlock(body=new_body))
