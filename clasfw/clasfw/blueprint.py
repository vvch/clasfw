from flask import Blueprint, current_app
from .models import Quantity, Amplitude

blueprint = Blueprint("clasfw", __name__,
    template_folder='templates',
    static_folder='static')


@blueprint.app_template_filter()
def cpx(value):
    """
    Format complex or real value or None
    """
    return "{:.2g}".format(value) if value else value


class qu:
    strfun_names = """
        R_T_00  R_L_00  R_TT_00  R_TL_00  R_TL'_00
    """.strip().split()
    strfuns = []
    amplitudes = []


@blueprint.before_app_first_request
def setup_quantities():
    qu.Q2, qu.W, qu.cos_theta, qu.phi, qu.dsigma, qu.Eb = (
        Quantity.query.filter_by(name=s).one()
            for s in "Q^2 W cos(theta) phi dsigma/dOmega E_b".split() )

    for s in qu.strfun_names:
        q = Quantity.query.filter_by(name=s).one()
        qu.strfuns.append(q)

    amplitudes_first_id = 200
    qu.amplitudes = Quantity.query.filter(
        # fixme: should NOT use plain numeric identifiers!
        Quantity.id.between(
            amplitudes_first_id,
            amplitudes_first_id+Amplitude.number)
    ).order_by(Quantity.id).all()


@blueprint.context_processor
def inject_qu():
    return dict(
        qu=qu,
        zip=zip)
