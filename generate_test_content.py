import os

# shoul be set in environment!
# may not behave as expected if set in code
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_APP', 'clasfw:app.py')

os.environ.setdefault('WERKZEUG_DEBUG_PIN', 'off') # no PIN for browser debugger

from clasfw.app import create_app
from clasfw.settings import DevConfig
from clasfw.models import Base, Model, Amplitude, Channel
from clasfw.extensions import db
import numpy as np


app = create_app(DevConfig)
# db.create_all()


with app.test_request_context():
    # Base.metadata.create_all()
    # db.create_all()
    m = Model(
        name="test",
        description="test model with dummy values",
        author="V. Mokeev")
    c1 = Channel(
        id=1,
        name="pi+ n",
        html=r"&pi;<sup>+</sup>n",
        tex=r"$\pi^+n$", )
    c2 = Channel(
        id=2,
        name="pi0 p",
        html=r"&pi;<sup>0</sup>p",
        tex=r"$\pi^0p$")

    w_all = np.linspace(0, 4, 10)
    q2_all = np.linspace(0, 5, 10)
    cos_theta_all = np.linspace(0, 1, 10)

    for q2 in q2_all:
        for w in w_all:
            print ("W, Q2 = ", w, q2)
            for cos_theta in cos_theta_all:
                a = Amplitude(
                    channel=c1,
                    w=w,
                    q2=q2,
                    cos_theta=cos_theta,
                )
                a.t1 = 3+5j
                m.amplitudes.append(a)
    db.session.add(m)
    db.session.add(c2)
    db.session.commit()
