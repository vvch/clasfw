from flask import request, render_template, abort
import numpy as np

import hep
import hep.amplitudes
from load_maid import MAIDObservables
from .blueprint import qu, blueprint as bp
from .models import Amplitude
from ..utils import equal_eps, tex


@bp.route('/compare')
def compare():
    channel_id= request.args.get('channel', type=int)
    model_id  = request.args.get('model', type=int)
    W         = request.args.get('w', type=float)
    Q2        = request.args.get('q2', type=float)
    Eb        = request.args.get('Eb', type=float, default=10.6)
    ds_index  = request.args.get('obs', type=int, default=0)

    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
    ).filter(
        equal_eps(Amplitude.w, W),
        equal_eps(Amplitude.q2, Q2),
    )

    # eps_T = hep.ε_T(W, Q2, Eb)
    # h=1

    ampls=ampl.all()
    if not ampls:
        abort(404)

    cos_theta_v = np.zeros(shape=(len(ampls),))
    sig_v = np.zeros(shape=(len(ampls),))

    for i, ampl in enumerate(ampls):
        cos_theta_v[i] = ampl.cos_theta
        ds = hep.amplitudes.ampl_to_R(ampl.H)*hep.amplitudes.R_to_dsigma_factors(ampl.w, ampl.q2)
        sig_v[i] = ds[ds_index]

    quantity = qu.dsigmas[ds_index]
    finalstate = ampl.channel

    maid = MAIDObservables.load_by_kinematics(Q2=Q2, W=W, FS=finalstate.name)
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
