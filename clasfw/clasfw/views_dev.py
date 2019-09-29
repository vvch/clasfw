from .blueprint import qu, blueprint as bp
from flask import current_app

from .models import Model, Amplitude, Channel, Quantity
from ..utils import equal_eps

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string, Markup, abort

import hep
import hep.amplitudes

from sqlalchemy import func, exc
from sqlalchemy.orm import exc
import numpy as np
import json


from ..extensions import db
from .forms import create_form


@bp.route('/form')
def interpolate_form():
    InterpolateForm = create_form(db.session, qu)
    form = InterpolateForm(request.args)

    # if form.validate() and form.submit.data:
    if form.submit.data:
        form.validate()
        # form.process()
        model = form.model.raw_data
        model = dir(form.model)
        model = form.model.data
        print('WWWWWWWWWW', model)
        return render_template_string(
            "{} <br> {} <br> {}".format(
                str(form.model),
                form.model.raw_data,
                # form.q2.min.data,
                form.model.data,
            )
        )
        return render_template("phi_dependence.html",
            ampl={},
            )

    return render_template("interpolate_form.html", form=form)


# @bp.route('/interpolate')
# def interpolate():
#     return render_template("interpolate_form.html", form=form)

