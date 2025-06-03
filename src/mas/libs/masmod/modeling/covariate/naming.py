import re


def make_parcov_varname(covariate_name: str, on_param_name: str) -> str:
    return f"{covariate_name}__{on_param_name}"


def split_parcov_varname(varname: str) -> tuple[str, str] | None:
    # {covariate_name}_{on_param_name}(_{index})?
    matched = re.match(r"(.+?)__(.+?)(?:_(\d+))?$", varname)

    if matched is None:
        return None

    return matched.group(1), matched.group(2)
