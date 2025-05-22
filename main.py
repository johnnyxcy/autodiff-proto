from sympy import exp

from functions.stats import normal_cdf
from module.defs.module import Module
from module.descriptor.distill import distill
from symbols._omega_eta import omega
from symbols._theta import theta
from utils.loggings import logger

logger.setLevel("DEBUG")


def add(a, b):
    return a + b


class MyDef(Module):
    def __init__(self, a, b, c):
        self.a = theta(a)
        self.b = omega(b)
        self.c = theta(c)
        self.d = omega(0.1)

    def pred(self):
        return add(self.a, self.b) + normal_cdf(self.c * exp(self.d))


if __name__ == "__main__":
    # Example usage
    my_def = MyDef(1, 2, 3)

    interpreted = distill(my_def)
