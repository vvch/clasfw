from clasfw.app import create_app, db
from clasfw import cli
from clasfw.models import Model, Quantity, Channel, Amplitude
from clasfw.clasfw.blueprint import qu

import numpy as np


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        'np': np,
        'db': db,
        'qu': qu,  #  fixme: not initialized 
        'Amplitude': Amplitude,
        'Quantity': Quantity,
        'Channel': Channel,
        'Model': Model,
    }
