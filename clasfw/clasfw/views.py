from .blueprint import blueprint as app
from flask import current_app

from clasfw.models import Model, Amplitude, Channel

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string

import numpy as np
import json


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/models')
def models_list():

    from sqlalchemy import func
    from clasfw.extensions import db

    sub_q = db.session.query(
        # Amplitude,
        Amplitude.model_id,
        func.count(Amplitude.model_id).label('count_ampl')
    ).group_by(Amplitude.model_id).subquery()

    # sub_q = Amplitude.query(
    # .model_id,
    #     func.count(Amplitude.model_id).label('count_ampl')
    # ).group_by(Amplitude.model_id).subquery()

    models = db.session.query(
        Model,
        Model.id,
        Model.name,
        Model.author,
        Model.description,
        sub_q.c.count_ampl
    ).join(
        sub_q, sub_q.c.model_id == Model.id
    ).all()

    # models = Model.query.join(Amplitude).with_entities(
    #     # func.count().label('count_ampl'),
    #     func.count(Amplitude.id).label('count_ampl')
    # ).all()

    return render_template('models_list.html',
        models=models)


@app.route('/model_data/<int:model_id>')
def model_data(model_id):
    channel = request.args.get('channel_id', None)
    model = Model.query.get(model_id)

    return render_template('model_data.html',
        model=model)
