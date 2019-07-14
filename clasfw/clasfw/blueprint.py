from flask import Blueprint, current_app

blueprint = Blueprint("clasfw", __name__,
    template_folder='templates',
    static_folder='static')

