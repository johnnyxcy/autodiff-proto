from api import (
    EvOneCmtLinear,
    OdeModule,
    column,
    compartment,
    exp,
    likelihood,
    normal_cdf,
    omega,
    theta,
)
from module.defs.ode import odeint
from module.descriptor.distill import distill
from syntax.unparse import unparse
from utils.loggings import logger

logger.setLevel("DEBUG")


# def add(a, b):
#     return a + b


def add(a, b):
    return a + b


# class MyDef(OdeModule):
#     def __init__(self):
#         super().__init__(odeint.DVERK(tol=1e-10))
#         self.pop_cl = theta(1.0)
#         self.pop_v = theta(10.0)
#         self.pop_ka = theta(1.0)
#         self.iiv_cl = omega(0.1)
#         self.iiv_v = omega(0.1)
#         self.iiv_ka = omega(0.1)
#         self.cmt1 = compartment()
#         self.cmt2 = compartment()

#         self.DV = column("DV")

#     def pred(self):
#         cl = self.pop_cl * exp(self.iiv_cl)
#         v = self.pop_v * exp(self.iiv_v)
#         ka = self.pop_ka * exp(self.iiv_ka)

#         k = cl / v
#         self.cmt1.dAdt = -ka * self.cmt1.A
#         self.cmt2.dAdt = ka * self.cmt1.A - k * self.cmt2.A
#         self.cmt1.alag = -k
#         self.cmt2.init_value = -ka
#         IPRED = self.cmt2.A / v
#         if IPRED < 0:
#             RES = add(self.DV, -IPRED)
#             CUM = normal_cdf(RES)
#             return likelihood(CUM)

#         return IPRED


class MyDef(EvOneCmtLinear.Physio):
    def __init__(self):
        super().__init__()
        self.pop_cl = theta(1.0)
        self.pop_v = theta(10.0)
        self.pop_ka = theta(1.0)
        self.iiv_cl = omega(0.1)
        self.iiv_v = omega(0.1)
        self.iiv_ka = omega(0.1)

    def pred(self):
        v = self.pop_v * exp(self.iiv_v)
        # F0 = (
        #     self.solve(
        #         cl=self.pop_cl * exp(self.iiv_cl),
        #         v=v,
        #         ka=self.pop_ka * exp(self.iiv_ka),
        #     )
        #     + 1
        # )

        # F = self.cmt_central.A / v
        F = self.solve(
            cl=self.pop_cl * exp(self.iiv_cl),
            v=v,
            ka=self.pop_ka * exp(self.iiv_ka),
            alag1=0.1,
        )

        IPRED = F

        return IPRED


if __name__ == "__main__":
    my_def = MyDef()
    # import libcst as cst

    #     mm = cst.parse_module("""def some():
    #     # This is a comment
    #     x = 1
    #     # some more comments
    #     x = 2
    # # Line of comment
    # """)

    #     print("11")

    interpreted = distill(my_def)

    print(unparse(interpreted._code_gen()))
