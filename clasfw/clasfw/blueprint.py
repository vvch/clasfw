from flask import Blueprint, current_app


blueprint = Blueprint("clasfw", __name__,
    template_folder='templates',
    static_folder='static')


@blueprint.app_template_filter()
def cpx(value):
    """
    Format complex or real value or None
    """
    return "{:.2g}".format(value) if value else value
