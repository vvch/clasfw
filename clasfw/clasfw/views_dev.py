from .blueprint import qu, blueprint as bp
from flask import current_app

from .models import Model, Amplitude, Channel, Quantity
from ..utils import equal_eps

from flask import request, Response, url_for, send_file, redirect, \
    render_template, render_template_string, Markup, abort

import hep
import hep.amplitudes
import hep.mandelstam

from sqlalchemy import func, exc
from sqlalchemy.orm import exc
import numpy as np
import scipy.interpolate
import json

from ..extensions import db
from .forms import create_form

from flask.views import MethodView


# fixme: temporary workaround
def ampl0_to_rfuncs(H0):
    H = np.concatenate(([None], H0))
    return hep.amplitudes.ampl_to_strfuns(H)

def ampl0_to_dsigma(Q2, W, eps_T, phi, h, H0):
    return strfuns_to_dsigma(
        Q2, W, eps_T, phi, h,
        ampl0_to_rfuncs(H0) )


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

    q = Amplitude.query.filter_by(
        channel=channel,
        model=model,
    )

    q_min = q.filter(field <= val).order_by(field.desc())
    q_max = q.filter(field >= val).order_by(field)

    return [
        q.limit(1).value(field)
            for q in (q_min, q_max) ]


def get_theta_dependence(model, channel, Q2, W, ds_index=0, qu_type='respfunc'):
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
    resf_v = np.zeros(shape=(len(ampls),))

    is_respfunc = qu_type=='respfunc'

    for i in range(len(ampls)):
        ampl = ampls[i]
        cos_theta_v[i] = ampl.cos_theta
        # ds = np.array(ampl.strfuns)*hep.amplitudes.R_to_dsigma_factors(ampl.q2, ampl.w)
        if is_respfunc:
            resf_v[i] = ampl.strfuns[ds_index]
        else:
            # fixme: temporary real part only
            resf_v[i] = ampl.H[ds_index+1].real  # "+1" here since ds_index starts from 0 but Amplitude.H starts from 1
    return cos_theta_v, resf_v


class InterpolateForm(BaseView):
    def prepare(self, *args, **kwargs):
        InterpolateForm = create_form(db.session, qu)
        form = InterpolateForm(request.args)

        if form.submit.data and form.validate():
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
                Amplitude.H1r, Amplitude.H1j,
                Amplitude.H2r, Amplitude.H2j,
                Amplitude.H3r, Amplitude.H3j,
                Amplitude.H4r, Amplitude.H4j,
                Amplitude.H5r, Amplitude.H5j,
                Amplitude.H6r, Amplitude.H6j,
            )
            t = np.array(list(data))
            if not len(t):
                abort(404)  #  TODO: more friendly and informative error message

            t = t.T

            # if form.varset.data == 'cos_theta':
            #     pass
            # elif form.varset.data == 'theta':
            #     t[2] = np.rad2deg(np.arccos(t[2]))  #  3rd column
            #     print(t[2])
            # elif form.varset.data == 't':
            #     print(t[2], t[1], t[0])
            #     t[2] = hep.mandelstam.cos_theta_to_t(t[2], t[1], t[0])  #  cos_theta, W, Q²
            #     print(t[2])
            #     print(t[2], t[1], t[0])


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

            ε = 0.00000001
            if form.varset.data == 'cos_theta':
                c_min  = form.cos_theta.min.data
                c_max  = form.cos_theta.max.data
                c_step = form.cos_theta.step.data
                cθ_source_qu = qu.cos_theta

                cθv_source = np.arange(c_min, c_max +ε, c_step)
                cθv = cθv_source
            elif form.varset.data == 'theta':
                c_min  = form.theta.min.data
                c_max  = form.theta.max.data
                c_step = form.theta.step.data
                cθ_source_qu = qu.theta

                cθv_source = np.arange(c_min, c_max +ε, c_step)
                cθv = np.cos(np.deg2rad(cθv_source))
            elif form.varset.data == 't':
                c_min  = form.t.min.data
                c_max  = form.t.max.data
                c_step = form.t.step.data
                cθ_source_qu = qu.t

                cθv_source = np.arange(c_min, c_max +ε, c_step)
                cθv = hep.mandelstam.t_to_cos_theta(cθv_source, w, q2)


            if 0:
                grid_q2, grid_w, grid_cθ = np.mgrid[
                    q2 : q2: 1j,
                    w  : w : 1j,
                    -1 : 1 : 0.1]
            else:
                grid_q2, grid_w, grid_cθ = np.array(np.meshgrid(
                    q2, w, cθv
                ))
                # )).transpose((0, 2, 1))

            # print('SHAPE OF POINTS', points.shape)
            # print(points)
            # print('SHAPE OF DATA', points.shape)
            # print(data)

            grid_R = scipy.interpolate.griddata(
                points, data,
                (grid_q2, grid_w, grid_cθ),
                method='linear')

            try:
                dsigma_index = qu.strfun_names.index(quantity.name)
                qu_type = 'respfunc'
            except ValueError:
                qu_type = 'amplitude'
                # dsigma_index = qu.amplitudes.index(quantity)  ## index starting from 0!
                # ##  fixme!!! can fail if loaded `quantity` session differs from `qu.amplitudes` section
                # ##  models.dictionarymixin.__eq__ should be implemented, comparing __class__, id or name
                dsigma_index = [
                    q.name for q in qu.amplitudes
                ].index(quantity.name)  ## fixme: temporary workaround

            # tmp
            # print('SHAPE1', grid_R.shape)
            # print(grid_R)

            if qu_type == 'respfunc':
                grid_R = np.apply_along_axis(
                    ampl0_to_rfuncs, 3, grid_R, #  3rd axis of grid_R with amplitudes
                    # np.sum, 3, grid_R,
                )
                grid_R = grid_R[:,:,:,dsigma_index]
            else:
                grid_R = grid_R[:,:,:,dsigma_index]
                # fixme: temporary real part only
                grid_R = grid_R.real

            # print('SHAPE2', grid_R.shape)


            self.plot = {
                'layout': {
                    # 'autosize': 'true',
                    'xaxis': {
                        'title': tex(cθ_source_qu),
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
                    'name': 'Interpolated, Q²={} GeV², W={} GeV'
                        .format(q2, w),
                    'x': cθv_source.tolist(),
                    'y': grid_R.flatten().tolist(),
                    'marker': {
                        'symbol': 'x-thin-open',
                        'size': 12,
                        'color': 'orange',
                        'line': {
                            'width': 3,
                        },
                    },
                }]
            }


            ## Comparison

            if 1:
                nearest_Q2_lo = q2
                nearest_Q2_hi = q2

                # nearest_Q2_lo, nearest_Q2_hi = get_value_neighbours(q2, model, channel)
                nearest_W_lo,  nearest_W_hi = get_value_neighbours(w, model, channel)

                cos_θ_lo_v, resf_lo_v = get_theta_dependence(model, channel,
                    q2, nearest_W_lo, dsigma_index, qu_type)
                cos_θ_hi_v, resf_hi_v = get_theta_dependence(model, channel,
                    q2, nearest_W_hi, dsigma_index, qu_type)

                if form.varset.data == 'theta':
                    cos_θ_lo_v = np.rad2deg(np.arccos(cos_θ_lo_v))[::-1]
                    cos_θ_hi_v = np.rad2deg(np.arccos(cos_θ_hi_v))[::-1]
                    resf_lo_v = resf_lo_v[::-1]
                    resf_hi_v = resf_hi_v[::-1]
                elif form.varset.data == 't':
                    cos_θ_lo_v = hep.mandelstam.cos_theta_to_t(
                        cos_θ_lo_v, nearest_W_lo, q2)
                    cos_θ_hi_v = hep.mandelstam.cos_theta_to_t(
                        cos_θ_hi_v, nearest_W_hi, q2)


                self.plot['data'] += [
                    {
                        'mode': 'markers',
                        'type': 'scatter',
                        'name': 'Nearest Q²={} GeV², W={} GeV'
                            .format(nearest_Q2_lo, nearest_W_lo),
                        'x': cos_θ_lo_v.tolist(),
                        'y': resf_lo_v.tolist(),
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
                        'x': cos_θ_hi_v.tolist(),
                        'y': resf_hi_v.tolist(),
                        'marker': {
                            'symbol': 'cross-thin-open',
                            'size': 12,
                            'color': 'green',
                            'line': {
                                'width': 3,
                            },
                        },
                    }
                ]


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
