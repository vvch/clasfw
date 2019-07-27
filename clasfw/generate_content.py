from .models import Model, Amplitude, Channel, Quantity, Unit
from .extensions import db
import hep.amplitudes
import numpy as np


def create_amplitude_qu(qu):
    tmpl_text = "<0 {}|T|{} {}>"
    tmpl_html = "&#x27e8;0&nbsp;{}|T|{}&nbsp;{}&#x27e9;"
    tmpl_tex  = "\\langle 0 \\; {}|T| {} \\; {}\\rangle"

    qq = []
    for i in range(hep.amplitudes.ampl_num):
        lambdas_str = tuple(
                hep.amplitudes.rlambda_to_str(l)
                    for l in hep.amplitudes.rlambdas_by_aindex(i))
        qq += Quantity(
            id = 200 + i,
            name = tmpl_text.format(*lambdas_str),
            html = tmpl_html.format(*lambdas_str),
            tex  = tmpl_tex.format(*lambdas_str),
            unit = qu.dimensionless,
        ),
    db.session.add_all(qq)
    return qu


def create_quantities_functions_qu(qu):
    qq = []
    dimensionless = Unit(
        id = 1,
        name = "dimensionless",
        html = "dimensionless",
        tex  = r"dimensionless",
        priority = -10,
    )
    qu.dimensionless = dimensionless
    rad = Unit(
        id = 2,
        name = "rad",
        html = "rad",
        tex  = r"rad",
        priority = -20,
    )
    deg = Unit(
        id = 3,
        name = "deg",
        html = "deg",
        tex  = r"deg",
        priority = -30,
    )
    GeV = Unit(
        id = 4,
        name = "GeV",
        html = "GeV",
        tex  = r"GeV",
        priority = -40,
    )
    GeV2 = Unit(
        id = 5,
        name = "GeV^2",
        html = "GeV²",
        tex  = r"GeV^2",
        priority = -50,
    )
    mcb = Unit(
        id = 6,
        name = "mcb",
        html = "μb",
        tex  = r"\mu b",
        priority = -60,
    )
    mcb_sr = Unit(
        id = 7,
        name = "mcb/sr",
        html = "μb/sr",
        tex  = r"\mu b /sr",
        priority = -70,
    )
    qq += Quantity(
        id = 191,
        name = "sigma_U",
        html = "&sigma;<sub>U</sub>",
        tex  = r"\sigma_{U}",
        priority = 100,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 44,
        name = "sigma_T",
        html = "&sigma;<sub>T</sub>",
        tex  = r"\sigma_{T}",
        priority = 90,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 43,
        name = "sigma_L",
        html = "&sigma;<sub>L</sub>",
        tex  = r"\sigma_{L}",
        priority = 80,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 47,
        name = "sigma_TT",
        html = "&sigma;<sub>TT</sub>",
        tex  = r"\sigma_{TT}",
        priority = 70,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 48,
        name = "sigma_TL",
        html = "&sigma;<sub>TL</sub>",
        tex  = r"\sigma_{TL}",
        priority = 60,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 666,
        name = "sigma_TL'",
        html = "&sigma;<sub>TL&prime;</sub>",
        tex  = r"\sigma_{TL'}",
        priority = 50,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 19,
        name = "dsigma/dOmega",
        html = "d&sigma;/d&Omega;",
        tex  = r"\mathrm{d}\sigma/\mathrm{d}\Omega",
        priority = 40,
        unit=mcb_sr,
    ),
    qq += Quantity(
        id = 1017,
        name = "cos(theta)",
        html = "cos(&theta;)",
        tex  = r"\cos(\theta)",
        priority = 30,
        unit=dimensionless,
    ),
    qq += Quantity(
        id = 1014,
        name = "Q^2",
        html = "Q<sup>2</sup>",
        tex  = r"Q^2",
        priority = 20,
        unit=GeV2,
    ),
    qq += Quantity(
        id = 1015,
        name = "W",
        html = "W",
        tex  = r"W",
        priority = 10,
        unit=GeV,
    ),
    qq += Quantity(
        id = 1016,
        name = "phi",
        html = "&phi;",
        tex  = r"\varphi",
        priority = 0,
        unit=rad,
    ),
    db.session.add_all(qq)
    return qu


def create_dictionaries():
    class qu:
        pass
    create_quantities_functions_qu(qu)
    create_amplitude_qu(qu)
    db.session.commit()


def generate_test_content():
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
                a1.a = [1 ]*hep.amplitudes.ampl_num
                a2.a = [1j]*hep.amplitudes.ampl_num
                a3.a0 = 3+5j
                a3.a1 = 1+2j
                m1.amplitudes.append(a1)
                m2.amplitudes.append(a2)
                m3.amplitudes.append(a3)
    db.session.add_all([m1, m2, m3])
    db.session.commit()


def generate_all():
    create_dictionaries()
    generate_test_content()


if __name__ == '__main__':
    from clasfw.app import create_app

    import os

    app = create_app()
    # db.create_all()
    with app.test_request_context():
        generate_all()
