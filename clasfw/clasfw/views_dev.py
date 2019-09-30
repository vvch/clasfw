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
import scipy.interpolate
import json


from ..extensions import db
from .forms import create_form



def tex(q):
    return "${}$".format(q.wu_tex)


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
        # data=0
        data = Amplitude.query.filter_by(
            model=model,
            channel=channel,
        ).values(
            Amplitude.q2,
            Amplitude.w,
            Amplitude.cos_theta,
            Amplitude.R_T,
        )
        t = np.array(list(data)).T
        # Q2_v, W_v, cos_θ, data = np.array(list(data)).T
        # Q2_v, W_v, cos_θ, data = np.array(list(data)).T
        Q2_v, W_v, cos_θ = t[0:3]
        cos_θ = cos_θ.copy()
        points = t[0:3].T
        data = t[3]


        # t = np.fromiter(list(data), "float,float,float,float")
        # t = np.fromiter(list(data), "f,f,f,f")
        # Q2_v, W_v, cos_θ, data = np.fromiter(list(data), "f,f,f,f").T
        # Q2_v, W_v, cos_θ, data = t
        # data = list(data)

        grid_q2, grid_w, grid_cθ = np.mgrid[
            q2 : q2: 1j,
            w  : w : 1j,
            -1 : 1 : 0.1]

        grid_R = scipy.interpolate.griddata(
            points, data,
            (grid_q2, grid_w, grid_cθ),
            method='linear')


        def get_theta_dependence(Q2, W, ds_index=0):
            ampl = Amplitude.query.filter_by(
                channel=channel,
                model=model,
            ).filter(
                equal_eps(Amplitude.q2, Q2),
                equal_eps(Amplitude.w, W),
            )

            ampls=ampl.all()
            if not ampls:
                abort(404)

            cos_theta_v = np.zeros(shape=(len(ampls),))
            sig_v = np.zeros(shape=(len(ampls),))

            ds_index = 0  ## R^00_T
            for i in range(len(ampls)):
                ampl = ampls[i]
                cos_theta_v[i] = ampl.cos_theta
                # ds = np.array(ampl.strfuns)*hep.amplitudes.R_to_dsigma_factors(ampl.q2, ampl.w)
                ds = ampl.strfuns
                sig_v[i] = ds[ds_index]
            return cos_theta_v.tolist(), sig_v.tolist()

        cos_θ_lo, resf_lo = get_theta_dependence(0.5, 1.5)
        cos_θ_hi, resf_hi = get_theta_dependence(0.5, 1.6)

        plot = {
            'layout': {
                # 'autosize': 'true',
                'xaxis': {
                    'title': tex(qu.cos_theta),
                },
                'yaxis': {
                    'title': tex(quantity),
                },
                'margin': {
                     't': 32,
                     # 'b': 65,
                     # 'l': 65,
                     # 'r': 50,
                },
            },
            'data': [{
                'mode': 'markers',
                'type': 'scatter',
                'name': 'Nearest Q², W',
                'x': cos_θ_lo,
                'y': resf_lo,
                'marker': {
                    'symbol': 'cross-thin-open',
                    'size': 12,
                    'line': {
                        'width': 3,
                    },
                },
            }, {
                'mode': 'markers',
                'type': 'scatter',
                'name': 'Nearest Q², W',
                'x': cos_θ_hi,
                'y': resf_hi,
                'marker': {
                    'symbol': 'cross-thin-open',
                    'size': 12,
                    'line': {
                        'width': 3,
                    },
                },
            }, {
                'mode': 'markers',
                'type': 'scatter',
                'name': 'Interpolated',
                'x': grid_cθ.flatten().tolist(),
                'y': grid_R.flatten().tolist(),
                'marker': {
                    'symbol': 'x-thin-open',
                    'size': 12,
                    'line': {
                        'width': 3,
                    },
                },
            }],
        }
        # ampl=ampls[-1]  # temporary, for template args

        Eb = 10.6
        return render_template('phi_dependence.html',
            plot=plot,
            Eb=Eb,
            # ampl=ampl,
            ampl={
                'model_id': model.id,
            },
            plot3D=True,
        )

        return render_template_string("""
            <dt>`model` var:</dt>
                <dd>{{ model }}</dd>
            <dt>`model` field:</dt>
                <dd>{{ form.model }}</dd>
            <dt>`form.model.data`:</dt>
                <dd>{{ form.model.data }}</dd>
            <dt>`form.model.raw_data`:</dt>
                <dd>{{ form.model.raw_data }}</dd>
            <dt>`grid_R`:</dt>
                <dd>{{ grid_R }}</dd>
            {#
            <dt>`form.is_submitted()`:</dt>
                <dd>{{ form.is_submitted() }}</dd>
            <dt>`form.validate_on_submit()`:</dt>
                <dd>{{ form.validate_on_submit() }}</dd>
            #}
            <dt>`data`</dt>
                <dd>{{ data }}</dd>
        """, form=form, model=model, data=data,
            grid_R=grid_R,
                # form.q2.min.data,
        )

    return render_template("interpolate_form.html", form=form)


# @bp.route('/interpolate')
# def interpolate():
#     return render_template("interpolate_form.html", form=form)

