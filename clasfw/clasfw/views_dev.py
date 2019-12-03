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

from flask.views import MethodView


# fixme: temporary workaround
def ampl0_to_strfuns(H0):
    H = np.concatenate(([None], H0))
    return hep.amplitudes.ampl_to_strfuns(H)

def ampl0_to_dsigma(Q2, W, eps_T, phi, h, H0):
    return strfuns_to_dsigma(
        Q2, W, eps_T, phi, h,
        ampl0_to_strfuns(H0) )


class BaseView(MethodView):
    # template = 'phi_dependence.html'
    template = 'interpolation_results.html'

    def get(self, *args, **kwargs):
        self.context = {}
        res = self.prepare(*args, **kwargs)
        if res is None:
            return render_template(
                self.template,
                **self.context
            )
        else:
            return res


    def prepare(self, *args, **kwargs):
        pass


    @classmethod
    def register_url(cls, app, rule, endpoint):
        return app.add_url_rule(rule, view_func=cls.as_view(endpoint)) 



def tex(q):
    return "${}$".format(q.wu_tex)


def get_value_neighbours(val, model, channel, field=None):
    if field is None:
        field = Amplitude.q2

    val_min = Amplitude.query.filter_by(
        channel=channel,
        model=model,
    ).filter(
        field <= val,
        # equal_eps(Amplitude.w, W),
    ).order_by(
        field.desc()
    ).limit(1).value(field)

    val_max = Amplitude.query.filter_by(
        channel=channel,
        model=model,
    ).filter(
        field >= val,
        # equal_eps(Amplitude.w, W),
    ).order_by(
        field
    ).limit(1).value(field)

    return val_min, val_max

def get_theta_dependence(model, channel, Q2, W, ds_index=0):
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

    # ds_index = 0  ## R^00_T
    for i in range(len(ampls)):
        ampl = ampls[i]
        cos_theta_v[i] = ampl.cos_theta
        # ds = np.array(ampl.strfuns)*hep.amplitudes.R_to_dsigma_factors(ampl.q2, ampl.w)
        ds = ampl.strfuns
        sig_v[i] = ds[ds_index]
    return cos_theta_v.tolist(), sig_v.tolist()


class InterpolateForm(BaseView):
    def prepare(self, *args, **kwargs):

        InterpolateForm = create_form(db.session, qu)
        form = InterpolateForm(request.args)

        if form.submit.data:
            model = form.model.data
            quantity = form.quantity.data
            channel = form.channel.data
            q2 = form.q2.data
            w = form.w.data

            data = Amplitude.query.filter_by(
                model=model,
                channel=channel,
            ).values(
                Amplitude.q2,
                Amplitude.w,
                Amplitude.cos_theta,
                # Amplitude.H1,
                Amplitude.H1r,
                Amplitude.H1j,
                Amplitude.H2r,
                Amplitude.H2j,
                Amplitude.H3r,
                Amplitude.H3j,
                Amplitude.H4r,
                Amplitude.H4j,
                Amplitude.H5r,
                Amplitude.H5j,
                Amplitude.H6r,
                Amplitude.H6j,
            )
            t = np.array(list(data)).T
            if not len(t):
                abort(404)

            # # Q2_v, W_v, cos_θ, data = np.array(list(data)).T
            # Q2_v, W_v, cos_θ = t[0:3]
            # cos_θ = cos_θ.copy()
            # points = t[0:3].T
            # data = t[3]

            points = t[0:3].T
            # data = np.array([
            #     np.complex(p, p)
            #         for p in t[3] ])
            # fixme: ugly temporary stub
            data = np.array([
                np.array([
                    complex(*c)
                        for c in
                            zip(*[iter(p)] * 2)  #  pairwise
                ])
                    for p in t[3:3+12].T ] )
                # complex(*p)
                # p[1]
                    # for p in t[3:3+2].T ] )

            # t = np.fromiter(list(data), "float,float,float,float")
            # t = np.fromiter(list(data), "f,f,f,f")
            # Q2_v, W_v, cos_θ, data = np.fromiter(list(data), "f,f,f,f").T
            # Q2_v, W_v, cos_θ, data = t
            # data = list(data)

            # q2 = 0.5
            # w  = 1.55

            # nearest_W_lo = 1.5
            # nearest_W_hi = 1.6
            nearest_Q2_lo = q2
            nearest_Q2_hi = q2

            # nearest_Q2_lo, nearest_Q2_hi = get_value_neighbours(q2, model, channel)
            nearest_W_lo,  nearest_W_hi = get_value_neighbours(w, model, channel)

            grid_q2, grid_w, grid_cθ = np.mgrid[
                q2 : q2: 1j,
                w  : w : 1j,
                -1 : 1 : 0.1]

            grid_R = scipy.interpolate.griddata(
                points, data,
                (grid_q2, grid_w, grid_cθ),
                method='linear')

            dsigma_index = {
                k:v for v,k in enumerate(qu.strfun_names)
            }[quantity.name]


            cos_θ_lo_v, resf_lo_v = get_theta_dependence(model, channel,
                nearest_Q2_lo, nearest_W_lo, dsigma_index)
            cos_θ_hi_v, resf_hi_v = get_theta_dependence(model, channel,
                nearest_Q2_lo, nearest_W_hi, dsigma_index)

            # tmp
            print('SHAPE1', grid_R.shape)
            if 1:
                grid_R = np.apply_along_axis(
                    ampl0_to_strfuns, 3, grid_R, #  3rd axis with amplitudes
                    # np.sum, 3, grid_R,
                )
                grid_R = grid_R[:,:,:,0]  #  only R_T
            else:
                grid_R = grid_R[:,:,:,0].imag  #  only H1
            print('SHAPE2', grid_R.shape)


            self.plot = {
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
                    'name': 'Nearest Q²={} GeV², W={} GeV'
                        .format(nearest_Q2_lo, nearest_W_lo),
                    'x': cos_θ_lo_v,
                    'y': resf_lo_v,
                    'marker': {
                        'symbol': 'cross-thin-open',
                        'size': 12,
                        'color': 'blue',
                        'line': {
                            'width': 3,
                        },
                    },
                }, {
                    'mode': 'markers',
                    'type': 'scatter',
                    'name': 'Nearest Q²={} GeV², W={} GeV'
                        .format(nearest_Q2_hi, nearest_W_hi),
                    'x': cos_θ_hi_v,
                    'y': resf_hi_v,
                    'marker': {
                        'symbol': 'cross-thin-open',
                        'size': 12,
                        'color': 'green',
                        'line': {
                            'width': 3,
                        },
                    },
                }, {
                    'mode': 'markers',
                    'type': 'scatter',
                    'name': 'Interpolated, Q²={} GeV², W={} GeV'
                        .format(q2, w),
                    'x': grid_cθ.flatten().tolist(),
                    # 'y': grid_R.flatten().imag.tolist(),
                    'y': grid_R.flatten().tolist(),
                    'marker': {
                        'symbol': 'x-thin-open',
                        'size': 12,
                        'color': 'orange',
                        'line': {
                            'width': 3,
                        },
                    },
                }],
            }

            self.context.update(
                plot=self.plot,
                # ampl=ampl,
                ampl={
                    'model': model,
                    'model_id': model.id,
                    'channel': channel,
                    'q2': q2,
                    'w': w,
                },
                plot3D=True,
            )
            return None

        return render_template("interpolate_form.html", form=form)


InterpolateForm.register_url(bp,
    '/interpolate', 'interpolate_form')
