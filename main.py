from sympy import exp

from functions.stats import normal_cdf
from module.defs.module import Module
from module.defs.ode import OdeModule
from module.descriptor.distill import distill
from symbols._ode import compartment
from symbols._omega_eta import omega
from symbols._theta import theta
from utils.loggings import logger

logger.setLevel("DEBUG")


def add(a, b):
    return a + b


class MyDef(OdeModule):
    def __init__(self, a, b, c):
        self.a = theta(a)
        self.b = omega(b)
        self.c = theta(c)
        self.d = omega(0.1)
        self.cmt1 = compartment()
        self.cmt2 = compartment()

    def pred(self):
        self.cmt1.dAdt = self.cmt1.A
        self.cmt2.dAdt = self.cmt1.A + self.cmt2.A
        return add(self.a, self.b) + normal_cdf(self.c * exp(self.d))


if __name__ == "__main__":
    # Example usage
    my_def = MyDef(1, 2, 3)

    interpreted = distill(my_def)
