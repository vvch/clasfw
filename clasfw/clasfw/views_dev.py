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


@bp.route('/interpolate')
def interpolate_form():
    InterpolateForm = create_form(db.session, qu)
    form = InterpolateForm(request.args)

    # if form.validate() and form.submit.data:
    if form.submit.data:
    # if form.is_submitted() and form.validate_on_submit():
        # form.validate()
        # form.validate_on_submit()
        # form.process()
        # model = form.model.raw_data
        # model = dir(form.model)
        model = form.model.data
        quantity = form.quantity.data
        channel = form.channel.data
        q2 = 0.52
        w  = 1.55
        data=0
        data = Amplitude.query.filter_by(
            model=model,
            channel=channel,
        ).values(
            Amplitude.q2,
            Amplitude.w,
            Amplitude.cos_theta,
            Amplitude.R_T,
        )
        Q2_v, W_v, cos_θ, data = np.array(list(data)).T
        # t = np.fromiter(list(data), "float,float,float,float")
        # t = np.fromiter(list(data), "f,f,f,f")
        # Q2_v, W_v, cos_θ, data = np.fromiter(list(data), "f,f,f,f").T
        # Q2_v, W_v, cos_θ, data = t
        # data = list(data)
        return render_template_string("""
            <dt>`model` var:</dt>
                <dd>{{ model }}</dd>
            <dt>`model` field:</dt>
                <dd>{{ form.model }}</dd>
            <dt>`form.model.data`:</dt>
                <dd>{{ form.model.data }}</dd>
            <dt>`form.model.raw_data`:</dt>
                <dd>{{ form.model.raw_data }}</dd>
            {#
            <dt>`form.is_submitted()`:</dt>
                <dd>{{ form.is_submitted() }}</dd>
            <dt>`form.validate_on_submit()`:</dt>
                <dd>{{ form.validate_on_submit() }}</dd>
            #}
            <dt>`data`</dt>
                <dd>{{ data }}</dd>
        """, form=form, model=model, data=data,
                # form.q2.min.data,
        )
        return render_template("phi_dependence.html",
            ampl={},
            )

    return render_template("interpolate_form.html", form=form)


# @bp.route('/interpolate')
# def interpolate():
#     return render_template("interpolate_form.html", form=form)

