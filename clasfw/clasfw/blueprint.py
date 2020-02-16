from functools import partial
from flask import Blueprint

import hep
import hep.amplitudes
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
    return "{:.3g}".format(value) if value else value


class qu:
    respfunc_names = ["R_{}_00".format(i) for i in hep.amplitudes.strfun_indexes]
    dsigma_names = ["dsigma_{}/dOmega".format(i) for i in hep.amplitudes.strfun_indexes]
    respfuncs = []
    dsigmas = []
    amplitudes = []  ##  amplitudes list starting from 0, e. g. amplitudes[0]==H1, etc...

    @classmethod
    def respfunc_index(cls, q: Quantity):
        return cls.respfunc_names.index(q.name)

    @classmethod
    def amplitude_index(cls, q: Quantity):
        # ##  fixme!!! can fail if loaded `quantity` session differs from `qu.amplitudes` section
        # ##  models.dictionarymixin.__eq__ should be implemented, comparing __class__, id or name
        return [  ## index starting from 0!
            qq.name for qq in cls.amplitudes
        ].index(q.name)  ## fixme: temporary workaround

    @classmethod
    def load(cls):
        cls.Q2, cls.W, cls.cos_theta, cls.theta, cls.xB, cls.t, cls.phi, cls.dsigma, cls.Eb = (
            Quantity.query.filter_by(name=s).one()
                for s in "Q^2 W cos(theta) theta x_B t phi dsigma/dOmega E_b".split() )
        cls.mcb_sr, cls.deg = (
            Unit.query.filter_by(name=s).one()
                for s in "mcb/sr deg".split() )

        for s in cls.respfunc_names:
            q = Quantity.query.filter_by(name=s).one()
            cls.respfuncs.append(q)

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
        hep=hep,
        partial=partial,
    )
