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


def tex(q):
    return "$${}$$".format(q.wu_tex)


@bp.route('/compare_maid')
def compare_maid():
    channel_id= request.args.get('channel', type=int)
    model_id  = request.args.get('model', type=int)
    Q2        = request.args.get('q2', type=float)
    W         = request.args.get('w', type=float)
    Eb        = request.args.get('Eb', type=float, default=10.6)
    ds_index  = request.args.get('obs', type=int, default=0)

    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
    ).filter(
        equal_eps(Amplitude.q2, Q2),
        equal_eps(Amplitude.w, W),
    )

    # eps_T = hep.ε_T(W, Q2, Eb)
    # h=1

    ampls=ampl.all()
    if not ampls:
        abort(404)

    cos_theta_v = np.zeros(shape=(len(ampls),))
    sig_v = np.zeros(shape=(len(ampls),))

    for i in range(len(ampls)):
        ampl = ampls[i]
        cos_theta_v[i] = ampl.cos_theta
        ds = np.array(ampl.strfuns)*hep.amplitudes.R_to_dsigma_factors(ampl.q2, ampl.w)
        sig_v[i] = ds[ds_index]

    quantity = qu.dsigmas[ds_index]
    finalstate = ampl.channel

    from load_maid import MAIDObservables
    maid = MAIDObservables.load_kinematics(Q2=Q2, W=W, FS=finalstate.name)
    maid_cos_theta = maid.keys()
    maid_sig = np.zeros(shape=(len(ampls),))
    for i, c in enumerate(maid_cos_theta):
        maid_sig[i] = maid[c][ds_index]

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
            'name': 'CLAS FW',
            'x': cos_theta_v.tolist(),
            'y': sig_v.tolist(),
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
            'name': 'MAID',
            'x': list(maid_cos_theta),
            'y': maid_sig.tolist(),
            'marker': {
                'symbol': 'x-thin-open',
                'size': 12,
                'line': {
                    'width': 3,
                },
            },
        }],
    }

    return render_template('phi_dependence.html',
        plot=plot,
        Eb=Eb,
        ampl=ampls[0],
    )
