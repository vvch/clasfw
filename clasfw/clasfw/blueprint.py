from flask import Blueprint, current_app
from .models import Quantity, Amplitude, Unit
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
    strfun_names = ["R_{}_00".format(i) for i in Amplitude.strfun_indexes]
    dsigma_names = ["dsigma_{}/dOmega".format(i) for i in Amplitude.strfun_indexes]
    strfuns = []
    dsigmas = []
    amplitudes = []

    @classmethod
    def load(cls):
        cls.Q2, cls.W, cls.cos_theta, cls.phi, cls.dsigma, cls.Eb = (
            Quantity.query.filter_by(name=s).one()
                for s in "Q^2 W cos(theta) phi dsigma/dOmega E_b".split() )
        cls.mcb_sr, = (
            Unit.query.filter_by(name=s).one()
                for s in "mcb/sr".split() )

        for s in cls.strfun_names:
            q = Quantity.query.filter_by(name=s).one()
            cls.strfuns.append(q)

        for s in cls.dsigma_names:
            q = Quantity.query.filter_by(name=s).one()
            cls.dsigmas.append(q)

        cls.amplitudes = Quantity.query.filter(
            Quantity.name.in_(
                'H_{}'.format(i)
                    for i in range(1, Amplitude.number+1)
            )
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
