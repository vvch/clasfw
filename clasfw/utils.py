import numpy as np
from sqlalchemy import func


def complex_format(c, real_f="{:f}", imag_f=None):
    if c is not None:
        if imag_f is not None:
            c = (real_f + ' ' + imag_f).format(c.real, c.imag)
        else:
            c = real_f.format(c)
    return "{}".format(c)


def np_linspace_left(start, stop, num=50, endpoint=True, dtype=None):
    return np.linspace(
        start=start, stop=stop, num=num+1,
        endpoint=endpoint, dtype=dtype)[1:]


def equal_eps(left, right, epsilon=0.000001):
    return func.abs(left - right) < epsilon
