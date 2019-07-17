from .blueprint import blueprint as app
from flask import current_app

from ..models import Model, Amplitude, Channel, Quantity

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string, Markup

from sqlalchemy import func
import numpy as np
import json


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/models')
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


@app.route('/model_data/<int:model_id>')
def model_data(model_id):
    channel = request.args.get('channel_id', None)
    model = Model.query.get(model_id)
    ampl_names = Quantity.query.filter(
        # fixme: should NOT use plain numeric identifiers!
        Quantity.id.between(200, 200+Amplitude.number-1)
    ).all()
    strfun_names = "σ<sub>U</sub>", "σ<sub>TT</sub>", "σ<sub>TL</sub>", "σ<sub>TL&prime;</sub>"
    strfun_names = tuple(map(Markup, strfun_names))
    # ampl_names = 'a0', 'a1', 'a2', 'a3', 'a4', 'a5'
    # strfun_names = "σ_U",  "σ_TT", "σ_TL", "σ_TL'"

    return render_template('model_data.html',
        model=model,
        ampl_names=tuple(ampl_names),
        strfun_names=strfun_names,
    )
