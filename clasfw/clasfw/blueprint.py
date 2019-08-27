from flask import Blueprint, current_app
from .models import Quantity, Amplitude
from ..utils import arxiv_url

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

    @classmethod
    def load(cls):
        cls.Q2, cls.W, cls.cos_theta, cls.phi, cls.dsigma, cls.Eb = (
            Quantity.query.filter_by(name=s).one()
                for s in "Q^2 W cos(theta) phi dsigma/dOmega E_b".split() )

        for s in cls.strfun_names:
            q = Quantity.query.filter_by(name=s).one()
            cls.strfuns.append(q)

        amplitudes_first_id = 200
        cls.amplitudes = Quantity.query.filter(
            # fixme: should NOT use plain numeric identifiers!
            Quantity.id.between(
                amplitudes_first_id,
                amplitudes_first_id+Amplitude.number)
        ).order_by(Quantity.id).all()


@blueprint.before_app_first_request
def setup_quantities():
    qu.load()


@blueprint.context_processor
def inject_qu():
    return dict(
        qu=qu,
        zip=zip,
        arxiv_url=arxiv_url,
    )
