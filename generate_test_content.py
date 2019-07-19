import os

# shoul be set in environment!
# may not behave as expected if set in code
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_APP', 'clasfw:app.py')

from clasfw.app import create_app
from clasfw.settings import DevConfig
from clasfw.models import Base, Model, Amplitude, Channel, Quantity
from clasfw.extensions import db
import numpy as np


def create_amplitude_qu():
    tmpl_text = "<0 {}|T|{} {}>"
    tmpl_html = "&#x27e8;0&nbsp;{}|T|{}&nbsp;{}&#x27e9;"
    tmpl_tex  = "\\langle 0 \\; {}|T| {} \\; {}\\rangle"

    qq = []
    for i in range(Amplitude.number):
        lambdas_str = tuple(
                Amplitude.lambda_int_to_str(l)
                    for l in Amplitude.lambdas_int_by_aindex(i))
        qq += Quantity(
            id = 200 + i,
            name = tmpl_text.format(*lambdas_str),
            html = tmpl_html.format(*lambdas_str),
            tex  = tmpl_tex.format(*lambdas_str),
        ),
    return qq


def create_structure_functions_qu():
    qq = []
    qq += Quantity(
        id = 191,
        name = "sigma_U",
        html = "&sigma;<sub>U</sub>",
        tex  = r"\sigma_{U}",
        priority = 100,
    ),
    qq += Quantity(
        id = 44,
        name = "sigma_T",
        html = "&sigma;<sub>T</sub>",
        tex  = r"\sigma_{T}",
        priority = 90,
    ),
    qq += Quantity(
        id = 43,
        name = "sigma_L",
        html = "&sigma;<sub>L</sub>",
        tex  = r"\sigma_{L}",
        priority = 80,
    ),
    qq += Quantity(
        id = 47,
        name = "sigma_TT",
        html = "&sigma;<sub>TT</sub>",
        tex  = r"\sigma_{TT}",
        priority = 70,
    ),
    qq += Quantity(
        id = 48,
        name = "sigma_TL",
        html = "&sigma;<sub>TL</sub>",
        tex  = r"\sigma_{TL}",
        priority = 60,
    ),
    qq += Quantity(
        id = 666,
        name = "sigma_TL'",
        html = "&sigma;<sub>TL&prime;</sub>",
        tex  = r"\sigma_{TL'}",
        priority = 50,
    ),
    return qq


def generate_test_content():
    # Base.metadata.create_all()
    # db.create_all()
    m1 = Model(
        name="test_1",
        description="test model with dummy amplitude values equal to 1",
        author="V. Mokeev")
    m2 = Model(
        name="test_i",
        description="test model with dummy amplitude values equal to i",
        author="V. Mokeev")
    m3 = Model(
        name="dummy",
        description="test model with dummy values",
        author="V. Chesnokov")
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

    def np_linspace_left(start, stop, num=50, endpoint=True, dtype=None):
        return np.linspace(
            start=start, stop=stop, num=num+1,
            endpoint=endpoint, dtype=dtype)[1:]

    w_all = np_linspace_left(0, 4, 8)
    q2_all = np_linspace_left(0, 5, 10)
    cos_theta_all = np.linspace(0, 1, 10, endpoint=False)

    for q2 in q2_all:
        for w in w_all:
            print ("W, Q2 = ", w, q2)
            for cos_theta in cos_theta_all:
                a1 = Amplitude(
                    channel=c1,
                    w=w,
                    q2=q2,
                    cos_theta=cos_theta,
                )
                a2 = Amplitude(
                    channel=c1,
                    w=w,
                    q2=q2,
                    cos_theta=cos_theta,
                )
                a3 = Amplitude(
                    channel=c2,
                    w=w,
                    q2=q2,
                    cos_theta=cos_theta,
                )
                a1.a = [1 ]*Amplitude.number
                a2.a = [1j]*Amplitude.number
                a3.a0 = 3+5j
                m1.amplitudes.append(a1)
                m2.amplitudes.append(a2)
                m3.amplitudes.append(a3)
    db.session.add_all(
        [m1, m2, m3] +
        create_amplitude_qu() +
        create_structure_functions_qu())
    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    # db.create_all()
    with app.test_request_context():
        generate_test_content()
