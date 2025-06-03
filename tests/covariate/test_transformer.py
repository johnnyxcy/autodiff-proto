import inspect

import libcst as cst
import polars as pl

from mas.libs.masmod.modeling.covariate.spec import (
    ContinuousCovariateInclusion,
)
from mas.libs.masmod.modeling.covariate.syntax.transformer import (
    CovariateInclusionTransformer,
)
from mas.libs.masmod.modeling.functions.math import exp
from mas.libs.masmod.modeling.symbols._column import column
from mas.libs.masmod.modeling.symbols._omega_eta import Eta
from mas.libs.masmod.modeling.symbols._theta import Theta
from mas.libs.masmod.modeling.syntax.unparse import unparse


def test_simple():
    class Simple:
        def __init__(self):
            self.tv_v = Theta("tv_v")
            self.iiv_cl = Eta("iiv_cl")
            self.iiv_v = Eta("iiv_v")

        def pred(self):
            tv_v = self.tv_v
            eta_v = self.iiv_v
            eta_cl = self.iiv_cl

            v = tv_v * exp(eta_v)
            cl = 0.134 * exp(eta_cl)

            k = cl / v
            return k

    instance = Simple()
    src = inspect.getsource(Simple).strip()
    transformer = CovariateInclusionTransformer(
        data=pl.DataFrame({"wt": [70, 80, 90]}),
        inclusions=[
            ContinuousCovariateInclusion(
                on=instance.tv_v,
                covariate=column("wt"),
                state="power",
            )
        ],
    )

    transformed = cst.MetadataWrapper(cst.parse_module(src)).visit(transformer)
    updated_src = unparse(transformed)
    print(updated_src)
