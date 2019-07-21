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
    strfun_names = "sigma_T", "sigma_L", "sigma_TT", "sigma_TL", "sigma_TL'"
    strfuns = []
    amplitudes = []


@blueprint.before_app_first_request
def setup_quantities():
    for s in qu.strfun_names:
        q = Quantity.query.filter_by(name=s).one()
        qu.strfuns.append(q)
    qu.dsigma = Quantity.query.filter_by(name='dsigma/dOmega').one()
    qu.amplitudes = Quantity.query.filter(
        # fixme: should NOT use plain numeric identifiers!
        Quantity.id.between(200, 200+Amplitude.number-1)
    ).order_by(Quantity.id).all()


@blueprint.context_processor
def inject_qu():
    return dict(
        qu=qu,
        zip=zip)
