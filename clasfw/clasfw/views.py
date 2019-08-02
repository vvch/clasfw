from .blueprint import qu, blueprint as bp
from flask import current_app

from .models import Model, Amplitude, Channel, Quantity

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string, Markup

import hep
import hep.hep
import hep.amplitudes

from sqlalchemy import func
import numpy as np
import json


@bp.route('/')
def index():

    return render_template('index.html')


@bp.route('/models')
def models_list():

    # from clasfw.extensions import db

    # sub_q = db.session.query(
    #     # Amplitude,
    #     Amplitude.model_id,
    #     func.count(Amplitude.model_id).label('count_ampl')
    # ).group_by(Amplitude.model_id).subquery()

    # sub_q = Amplitude.query(
    # .model_id,
    #     func.count(Amplitude.model_id).label('count_ampl')
    # ).group_by(Amplitude.model_id).subquery()

    # models = db.session.query(
    #     Model,
    #     Model.id,
    #     Model.name,
    #     Model.author,
    #     Model.description,
    #     sub_q.c.count_ampl
    # ).join(
    #     sub_q, sub_q.c.model_id == Model.id
    # ).all()

    models = Model.query.join(
        Amplitude
    ).group_by(Model.id).add_columns(
        # func.count().label('count_ampl'),
        func.count(Amplitude.id).label('count_ampl'),
    # ).with_entities(
    #     Model,
    #     # func.count().label('count_ampl'),
    #     func.count(Amplitude.id).label('count_ampl')
    ).all()

    # models = Model.query.add_columns(Model.id.label('count_ampl')).all()
    # print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
    # m0 = models[0]
    # print(type(m0))
    # print(dir(m0))
    # print(dir(m0.Model))
    # print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')

    return render_template('models_list.html',
        models=models)


@bp.route('/model_data/<int:model_id>')
def model_data(model_id):
    channel = request.args.get('channel_id', None)
    model = Model.query.get(model_id)

    return render_template('model_data.html',
        model=model,
    )


def plotly_3dlabel(q):
    try:
        return q.unicode
    except AttributeError:
        try:
            return q.name
        except AttributeError:
            pass
    return q.name

def tex(q):
    return "${}$".format(q.wu_tex)


@bp.route('/dsigma')
def phi_dependence():
    channel_id= request.args.get('channel_id', type=int)
    model_id  = request.args.get('model_id', type=int)
    Q2        = request.args.get('q2', type=float)
    Q2        = request.args.get('q2', type=float)
    W         = request.args.get('w', type=float)
    cos_theta = request.args.get('cos_theta', type=float, default=None)
    Eb        = request.args.get('Eb', type=float, default=10.6)

    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
        q2=Q2,
        w=W,
    )

    plot3D = cos_theta is None

    phi = np.linspace(0, 2*np.pi)
    eps_T = hep.hep.ε_T(W, Q2, Eb)


    if not plot3D:
        ampl = ampl.filter_by(
            cos_theta=cos_theta,
        ).one()
        sig = hep.amplitudes.strfuns_to_dsigma(W, Q2, cos_theta, eps_T, phi, *(ampl.strfuns))

        plot = {
            'layout': {
                # 'autosize': 'true',
                'xaxis': {
                    'title': tex(qu.phi),
                },
                'yaxis': {
                    'title': tex(qu.dsigma),
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
                'x': phi.tolist(),
                'y': sig.tolist(),
            }],
        }
    else:  #  3D-plot
        ampls=ampl.all()
        sig_M = np.zeros(shape=(len(ampls), len(phi)))
        cos_theta_v = np.zeros(shape=(len(ampls),))

        for i in range(len(ampls)):
            ampl = ampls[i]
            cos_theta = ampl.cos_theta
            cos_theta_v[i] = ampl.cos_theta
            sig = hep.amplitudes.strfuns_to_dsigma(W, Q2, cos_theta, eps_T, phi, *(ampl.strfuns))
            sig_M[i] = sig

        # i = np.arange(len(ampls))
        # sig_M[i] = hep.amplitudes.strfuns_to_dsigma(W, Q2, cos_theta, eps_T, phi, *(ampl[i].strfuns))

        plot = {
            'layout': {
                'scene': {
                    # 'autosize': 'true',
                    'xaxis': {
                        'title': "φ, rad",  # fixme!
                    },
                    'yaxis': {
                        # 'title': plotly_3dlabel(qu.cos_theta),
                        'title': "cos θ",  # fixme!
                    },
                    'zaxis': {
                        # 'title': plotly_3dlabel(qu.dsigma),
                        'title': "dσ/dΩ, μb/sr",  # fixme!
                        'rangemode': 'tozero',
                    },
                },
            },
            'data': [{
                # 'mode': 'markers',
                'type': 'surface',
                'x': phi.tolist(),
                'y': cos_theta_v.tolist(),
                'z': sig_M.tolist(),
            }],
        }
        ampl=ampls[-1]  # temporary, for template args

    return render_template('phi_dependence.html',
        plot=plot,
        Eb=Eb,
        ampl=ampl,
        plot3D=plot3D,
    )
