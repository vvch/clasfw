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
        func.count(Amplitude.id).label('count_ampl'),
        func.min(Amplitude.q2).label('q2_min'),
        func.max(Amplitude.q2).label('q2_max'),
        func.min(Amplitude.w).label('w_min'),
        func.max(Amplitude.w).label('w_max'),
    ).all()

    by_model_id = {}
    for mm in models:
        m = mm.Model
        prop = {}
        by_model_id[m.id] = prop
        prop['channels'] = Channel.query.distinct().join(Amplitude).filter(Amplitude.model==m)
        # prop['count_ampl'] = Amplitude.query.filter_by(model=m).count()
        # prop['count_ampl'] = Amplitude.query.filter_by(model=m).value( func.count(Amplitude.id) )

    # models = Model.query.add_columns(Model.id.label('count_ampl')).all()
    # print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')
    # m0 = models[0]
    # print(type(m0))
    # print(dir(m0))
    # print(dir(m0.Model))
    # print('WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW')

    return render_template('models_list.html',
        models=models,
        by_model_id=by_model_id)


@bp.route('/model/<int:model_id>')
@bp.route('/model/<int:model_id>/p<int:page>')
def model_data(model_id, page=1):
    channel = request.args.get('channel', None)
    q2 = request.args.get('q2', default=None, type=float)
    model = Model.query.get_or_404(model_id)
    if channel:
        channel = Channel.query.get_or_404(channel)

    amplitudes = Amplitude.query.filter_by(model_id=model.id)
    if channel or q2:
        if channel:
            amplitudes = amplitudes.filter_by(channel_id=channel.id)
        if q2:
            amplitudes = amplitudes.filter(equal_eps(Amplitude.q2, q2))
    amplitudes = amplitudes.order_by(
        Amplitude.channel_id,  ##  fixme: use channel.priority
        Amplitude.q2,
        Amplitude.w,
        Amplitude.cos_theta.desc(),
    )
    # amplitudes = amplitudes.all()
    amplitudes = amplitudes.paginate(page, current_app.config['RECORDS_PER_PAGE'])

    return render_template('model_data.html',
        model=model,
        channel=channel,
        q2=q2,
        amplitudes=amplitudes,
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
    return "$${}$$".format(q.wu_tex)


@bp.route('/dsigma')
def phi_dependence():
    channel_id= request.args.get('channel', type=int)
    model_id  = request.args.get('model', type=int)
    Q2        = request.args.get('q2', type=float)
    W         = request.args.get('w', type=float)
    cos_theta = request.args.get('cos_theta', type=float, default=None)
    Eb        = request.args.get('Eb', type=float, default=10.6)

    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
    ).filter(
        equal_eps(Amplitude.q2, Q2),
        equal_eps(Amplitude.w, W),
    )

    phi = np.linspace(0, 2*np.pi)
    eps_T = hep.ε_T(W, Q2, Eb)
    h=1

    if cos_theta is not None:  #  2D slice plot
        try:
            ampl = ampl.filter(
                equal_eps(Amplitude.cos_theta, cos_theta),
            ).one()
        except exc.NoResultFound:
            abort(404)

        respfuncs = hep.amplitudes.ampl_to_strfuns(ampl.H)
        sig = hep.amplitudes.strfuns_to_dsigma(
            Q2, W, eps_T, phi, h, respfuncs)

        plot = {
            'layout': {
                # 'autosize': 'true',
                'xaxis': {
                    'title': tex(qu.phi),
                    # 'ticktext': [0, 1, '$\\frac{\\pi}{2}$', 2, 3, '$\\pi$', 4, '$\\frac{3\\pi}{2}$', 5, 6, '$2\\pi$'],
                    # 'tickvals': [0, 1, np.pi/2,             2, 3, np.pi,    4, 3*np.pi/2,            5, 6, 2*np.pi],
                },
                'yaxis': {
                    'title': tex(qu.dsigma),
                    'rangemode': 'tozero',
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

        return render_template('phi_dependence.html',
            plot=plot,
            Eb=Eb,
            ampl=ampl,
            respfuncs=respfuncs,
            dsigmas=respfuncs*hep.amplitudes.R_to_dsigma_factors(ampl.q2, ampl.w),
        )
    else:  #  3D-plot
        ampls=ampl.all()
        if not ampls:
            abort(404)
        sig_M = np.zeros(shape=(len(ampls), len(phi)))
        cos_theta_v = np.zeros(shape=(len(ampls),))

        for i in range(len(ampls)):
            ampl = ampls[i]
            cos_theta = ampl.cos_theta
            cos_theta_v[i] = ampl.cos_theta
            sig = hep.amplitudes.strfuns_to_dsigma(
                Q2, W, eps_T, phi, h,
                hep.amplitudes.ampl_to_strfuns(ampl.H))
            sig_M[i] = sig

        # i = np.arange(len(ampls))
        # sig_M[i] = hep.amplitudes.strfuns_to_dsigma(
            # Q2, W, eps_T, phi, *(ampl[i].strfuns))

        plot = {
            'layout': {
                'autosize': 'true',
                'width':  1000,
                'height': 800,

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
                'hovertemplate':
                    "φ: %{x} rad<br>"
                    "cos<i>θ</i>: %{y}<br>"
                    "dσ/dΩ: %{z} μb/sr"
                    "<extra></extra>",
            }],
        }

        return render_template('phi_dependence_3D.html',
            plot=plot,
            Eb=Eb,
            ampl=ampls[0],
        )


@bp.route('/groups')
@bp.route('/groups/p<int:page>')
def groups_list(page=1):
    models = Amplitude.query.join(
        Model, Channel
    ).group_by(
        Model.id, Channel.id, Amplitude.q2
    ).add_columns(
        func.count(Amplitude.id).label('count_ampl'),
        func.min(Amplitude.w).label('w_min'),
        func.max(Amplitude.w).label('w_max'),
    ).order_by(
        # Model.priority.desc(),
        Model.id, # fixme: temporary, use priority
        # Channel.priority.desc(),
        Channel.id, # fixme: temporary
        Amplitude.q2,
    ).paginate(page, current_app.config['RECORDS_PER_PAGE'])

    return render_template('groups_list.html',
        models=models)
