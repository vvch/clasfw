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


@bp.route('/phi')
def phi_dependence():
    model_id, channel_id, q2, w, cos_theta = (
        request.args.get(x)
            for x in "model_id channel_id q2 w cos_theta".split()
    )
    q2, w, cos_theta = [float(x) for x in (q2, w, cos_theta)]
    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
        q2=q2,
        w=w,
        cos_theta=cos_theta,
    ).one()

    phi = np.linspace(0, 2*np.pi)
    # test dummy data
    # sig = np.sin(phi)
    eps_T = hep.hep.ε_T(w, q2, 10.6)  # Eb = 10.6 GeV
    sig = hep.amplitudes.strfuns_to_dsigma(w, q2, cos_theta, eps_T, phi, *(ampl.strfuns))

    def tex(q):
        return "${}$".format(q.tex)

    plot = {
        'layout': {
            # 'autosize': 'true',
            'xaxis': {
                'title': tex(qu.phi),
            },
            'yaxis': {
                'title': tex(qu.dsigma),
            },
        },
        'data': [{
            'mode': 'markers',
            'type': 'scatter',
            'x': phi.tolist(),
            'y': sig.tolist(),
        }],
    }

    return render_template('phi_dependence.html',
        ampl=ampl,
        plot=plot,
    )


@bp.route('/dsigma')
def dsigma():
    model_id, channel_id, q2, w = (
        request.args.get(x)
            for x in "model_id channel_id q2 w".split()
    )
    q2, w = [float(x) for x in (q2, w)]
    ampls = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
        q2=q2,
        w=w,
    ).all()

    phi = np.linspace(0, 2*np.pi)
    # test dummy data
    # sig = np.sin(phi)
    eps_T = hep.hep.ε_T(w, q2, 10.6)  # Eb = 10.6 GeV
    sig_M = np.zeros(shape=(len(ampls), len(phi)))
    cos_theta_v = np.zeros(shape=(len(ampls),))
    # for a in ampls:
    for i in range(len(ampls)):
        ampl = ampls[i]
        cos_theta = ampl.cos_theta
        cos_theta_v[i] = ampl.cos_theta
        sig = hep.amplitudes.strfuns_to_dsigma(w, q2, cos_theta, eps_T, phi, *(ampl.strfuns))
        sig_M[i] = sig

    # i = np.arange(len(ampls))
    # sig_M[i] = hep.amplitudes.strfuns_to_dsigma(w, q2, cos_theta, eps_T, phi, *(ampl[i].strfuns))

    def plotly_3dlabel(q):
        try:
            return q.unicode
        except AttributeError:
            try:
                return q.name
            except AttributeError:
                pass
        return q.name

    plot = {
        'layout': {
            'scene': {
                # 'autosize': 'true',
                'xaxis': {
                    'title': "ϕ",
                },
                'yaxis': {
                    # 'title': plotly_3dlabel(qu.cos_theta),
                    'title': "cos θ",
                },
                'zaxis': {
                    # 'title': plotly_3dlabel(qu.dsigma),
                    'title': "dσ/dΩ",
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

    return render_template('phi_dependence.html',
        kinem=ampl, # temporary
        plot=plot,
    )
