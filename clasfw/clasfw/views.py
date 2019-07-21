from .blueprint import qu, blueprint as bp
from flask import current_app

from .models import Model, Amplitude, Channel, Quantity

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string, Markup

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
    ampl = Amplitude.query.filter_by(
        channel_id=channel_id,
        model_id=model_id,
        q2=q2,
        w=w,
        cos_theta=cos_theta,
    ).one()

    phi = np.linspace(0, 2*np.pi)
    # test dummy data
    sig = np.sin(phi)

    plot = {
        'layout': {
            # 'autosize': 'true',
            'xaxis': {
                'title': r'$\varphi$',
            },
            'yaxis': {
                'title': "${}$".format(qu.dsigma.tex),
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
