import numpy as np
from sqlalchemy import func
import re
import json


def complex_format(c, real_f="{:f}", imag_f=None):
    if c is not None:
        if imag_f is not None:
            c = (real_f + ' ' + imag_f).format(c.real, c.imag)
        else:
            c = real_f.format(c)
    return "{}".format(c)


def equal_eps(left, right, epsilon=0.000001):
    return func.abs(left - right) < epsilon


def to_json(obj, **kvargs):
    class npJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj)
    return json.dumps(obj, cls=npJSONEncoder, **kvargs)


def arxiv_url(arxiv):
    m = re.search(r"arXiv:((?:\w+\-?\w+/)?\d+\.?\d+)", arxiv, re.I)
    if m:
        a = m.group(1)
        return "https://arxiv.org/abs/" + a
    raise ValueError('Not an arXiv link')

