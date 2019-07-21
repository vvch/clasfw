from .models import Model, Quantity, Channel, Amplitude

import numpy as np


def get_shell_context():
    return {
        'Amplitude': Amplitude,
        'Quantity': Quantity,
        'Channel': Channel,
        'Model': Model,
        'np': np,
    }
