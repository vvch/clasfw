import numpy as np

import hep.amplitudes
from .models import Model, Amplitude, Channel, Quantity, Unit
from .extensions import db


def create_amplitude_qu(qu):
    H_tmpl_text = "H_{}"
    H_tmpl_html = "H<sub>{}</sub>"
    H_tmpl_tex  = "H_{{{}}}"
    H_start_id  = 200

    for i in range(1, Amplitude.number+1):
        db.session.add(Quantity(
            id = H_start_id + i,
            name = H_tmpl_text.format(i),
            html = H_tmpl_html.format(i),
            tex  = H_tmpl_tex.format(i),
            unit = qu.GeVm1,
            priority=-(H_start_id+i),
        ))

    R_tmpl_text = "R_{}_00"
    R_tmpl_html = "R<span class='supsub'><sup>00</sup><sub>{}</sub></span>"
    R_tmpl_tex  = "R_{{{}}}^{{00}}"

    s_tmpl_text = "dsigma_{}/dOmega"
    s_tmpl_html = "d&sigma;<sub>{}</sub>/d&Omega;"
    s_tmpl_tex  = "\\frac{{d\\sigma_{{{0}}}}}{{d\\Omega}}"

    R_start_id  = 300
    s_start_id  = 400

    for ii, i in enumerate(hep.amplitudes.strfun_indexes):
        hi = i.replace("'", "&prime;")
        db.session.add_all([
            Quantity(
                id   = R_start_id + ii,
                name = R_tmpl_text.format(i),
                html = R_tmpl_html.format(hi),
                tex  = R_tmpl_tex.format(i),
                # unit = qu.GeVm2,
                unit = qu.mcb_sr,
                priority    = -(R_start_id+ii),
                description = "Response function",
            ),
            Quantity(
                id   = s_start_id + ii,
                name = s_tmpl_text.format(i),
                html = s_tmpl_html.format(hi),
                tex  = s_tmpl_tex.format(i),
                unit = qu.mcb_sr,
                priority    = -(s_start_id+ii),
                description = "Interference term",
            ),
        ])


def create_quantities_functions_qu(qu):
    qq = []
    qu.dimensionless = Unit(
        id = 1,
        name = "dimensionless",
        html = "dimensionless",
        tex  = r"dimensionless",
        priority = -10,
    )
    qu.rad = Unit(
        id = 2,
        name = "rad",
        html = "rad",
        tex  = r"rad",
        priority = -20,
    )
    qu.deg = Unit(
        id = 3,
        name = "deg",
        html = "deg",
        tex  = r"deg",
        priority = -30,
    )
    qu.GeV = Unit(
        id = 4,
        name = "GeV",
        html = "GeV",
        tex  = r"GeV",
        priority = -40,
    )
    qu.GeV2 = Unit(
        id = 5,
        name = "GeV^2",
        html = "GeV²",
        tex  = r"GeV^2",
        priority = -50,
    )
    qu.mcb = Unit(
        id = 6,
        name = "mcb",
        html = "μb",
        tex  = r"\mu b",
        priority = -60,
    )
    qu.mcb_sr = Unit(
        id = 7,
        name = "mcb/sr",
        html = "μb/sr",
        tex  = r"\mu b/sr",
        priority = -70,
    )
    qu.GeVm1 = Unit(
        id = 8,
        name = "GeV^-1",
        html = "GeV<sup>&minus;1</sup>",
        tex  = r"GeV^{-1}",
        priority = -80,
    )
    qu.GeVm2 = Unit(
        id = 9,
        name = "GeV^-2",
        html = "GeV<sup>&minus;2</sup>",
        tex  = r"GeV^{-2}",
        priority = -90,
    )

    qq += Quantity(
        id = 19,
        name = "dsigma/dOmega",
        html = "d&sigma;/d&Omega;",
        tex  = r"\frac{\mathrm{d}\sigma}{\mathrm{d}\Omega}",
        description = "Differential cross-section",
        priority = 50,
        unit=qu.mcb_sr,
    ),
    qq += Quantity(
        id = 1014,
        name = "Q^2",
        html = "Q<sup>2</sup>",
        tex  = r"Q^2",
        description = "Photon virtuality",
        priority = 20,
        unit=qu.GeV2,
    ),
    qq += Quantity(
        id = 1015,
        name = "W",
        html = "W",
        tex  = r"W",
        description = "Invariant mass of the final hadronic system",
        priority = 10,
        unit=qu.GeV,
    ),
    qq += Quantity(
        id = 1013,
        name = "x_B",
        html = "x<sub>B</sub>",
        tex  = r"x_B",
        description = "Bjorken variable",
        priority = 5,
        unit=qu.dimensionless,
    ),
    qq += Quantity(
        id = 1016,
        name = "phi",
        html = "&phi;",
        tex  = r"\varphi",
        priority = 0,
        unit=qu.rad,
    ),
    qq += Quantity(
        id = 1017,
        name = "cos(theta)",
        html = '<span class="op">cos</span>&theta;',
        tex  = r"\cos\theta",
        priority = 30,
        unit=qu.dimensionless,
    ),
    qq += Quantity(
        id = 1018,
        name = "theta",
        html = '&theta;',
        tex  = r"\theta",
        priority = 40,
        unit=qu.rad,
    ),
    qq += Quantity(
        id = 1666,
        name = "E_b",
        html = "E<sub>b</sub>",
        tex  = r"E_{b}",
        description = "Beam energy",
        priority = -10,
        unit=qu.GeV,
    ),
    qq += Quantity(
        id = 1667,
        name = "t",
        html = 't',
        tex  = r"t",
        priority = -20,
        unit=qu.GeV2,
        description="Mandelstam variable t",
    ),
    db.session.add_all(qq)
    db.session.add(qu.deg)  # not linked to any quantity as default unit
    return qu


def create_dictionaries(verbose=0):
    if verbose >=0:
        print("Generating dictionaries...")
    class qu:
        pass
    create_quantities_functions_qu(qu)
    create_amplitude_qu(qu)
    db.session.commit()


def generate_test_content(verbose=0):
    if verbose >=0:
        print("Generating test content...")
    m1 = Model(
        name="test_1",
        description="test model with dummy amplitude values equal to 1",
        author="V. Mokeev")
    m2 = Model(
        name="test_i",
        description="test model with dummy amplitude values equal to i",
        author="V. Mokeev")
    # m3 = Model(
    #     name="dummy",
    #     description="test model with dummy values",
    #     author="V. Chesnokov")
    c1 = Channel(
        id=1,
        name="pi+ n",
        html=r"&pi;<sup>+</sup>n",
        tex=r"$\pi^+n$",
        priority=0 )
    c2 = Channel(
        id=2,
        name="pi0 p",
        html=r"&pi;<sup>0</sup>p",
        tex=r"$\pi^0p$",
        priority=-10 )
    c3 = Channel(
        id=22,
        name="pi- p",
        html=r"&pi;<sup>&minus;</sup>p",
        tex=r"$\pi^-p$",
        priority=-20 )
    c4 = Channel(
        id=23,
        name="pi0 n",
        html=r"&pi;<sup>0</sup>n",
        tex=r"$\pi^0n$",
        priority=-30 )

    ε = 0.00001
    w_all     = np.arange( 1.1, 4.0 +ε, 0.1)
    q2_all    = np.arange( 0.0, 8.0 +ε, 0.5)
    cos_θ_all = np.arange(-1.0, 1.0 +ε, 0.1)
    cos_θ_all = np.array([  ##  drop insignificant fluctuations
        0 if np.isclose(_, 0) else _
            for _ in cos_θ_all
    ])

    for ch in c1, c2, c3, c4:
      for q2 in q2_all:
        if verbose>0:
            # TODO: use logger instead of print
            print ("Q2 = ", q2)
        for w in w_all:
            if verbose>1:
                # TODO: use logger instead of print
                print ("\tW = ", w)
            for cos_θ in cos_θ_all:
                a1 = Amplitude(
                    channel=ch,
                    w=w,
                    q2=q2,
                    cos_theta=cos_θ,
                )
                a2 = Amplitude(
                    channel=ch,
                    w=w,
                    q2=q2,
                    cos_theta=cos_θ,
                )
                # a3 = Amplitude(
                #     channel=ch,
                #     w=w,
                #     q2=q2,
                #     cos_theta=cos_θ,
                # )
                a1.H = [1 ]*Amplitude.number
                a2.H = [1j]*Amplitude.number
                # a3.H1 = [1, -1, -1, 1, -1, 1]
                m1.amplitudes.append(a1)
                m2.amplitudes.append(a2)
                # m3.amplitudes.append(a3)
    db.session.add_all([m1, m2])
    if verbose >=0:
        print("Committing results to the database...")
    db.session.commit()


def generate_all(verbose=0):
    create_dictionaries()
    generate_test_content(verbose)


if __name__ == '__main__':
    from clasfw.app import create_app

    app = create_app()
    # db.create_all()
    with app.test_request_context():
        generate_all()
