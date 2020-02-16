import copy
from flask import current_app
from flask import request, render_template, abort
from flask.views import MethodView

import numpy as np
import scipy.interpolate

import hep
import hep.amplitudes
import hep.mandelstam
from load_maid import MAIDData
from .blueprint import qu, blueprint as bp
from .models import Amplitude
from ..utils import equal_eps, to_json
from ..extensions import db
from .forms import create_form


def tex(q):
    return "${}$".format(q.wu_tex)


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
        return res

    def prepare(self, *args, **kwargs):
        pass

    @classmethod
    def register_url(cls, app, rule, endpoint):
        return app.add_url_rule(rule, view_func=cls.as_view(endpoint))


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
        return np.array([]), np.array([])

    cos_theta_v = np.zeros(shape=(len(ampls),))
    resf_v = np.zeros(shape=(len(ampls),))

    is_respfunc = qu_type=='respfunc'

    for i, ampl in enumerate(ampls):
        cos_theta_v[i] = ampl.cos_theta
        if is_respfunc:
            resf_v[i] = hep.amplitudes.ampl_to_R(ampl.H)[ds_index]
        else:
            # fixme: temporary real part only
            resf_v[i] = ampl.H[ds_index].real
    return cos_theta_v, resf_v


class InterpolateFormView(BaseView):
    def prepare(self, *args, **kwargs):
        InterpolateForm = create_form(db.session, qu)
        form = InterpolateForm(request.args)

        if form.submit.data and form.validate():
            self.create_plot(form)
            self.context.update(
                plot=to_json(self.plot,
                    indent=(4 if current_app.debug else None) ),
            )
            return None

        return render_template("interpolate_form.html", form=form)

    def create_plot(self, form):
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
                cθ_source_qu = copy.deepcopy(qu.theta)
                cθ_source_qu.unit = qu.deg

                cθv_source = np.arange(c_min, c_max +ε, c_step)
                cθv = np.cos(np.deg2rad(cθv_source))
            elif form.varset.data == 't':
                c_min  = form.t.min.data
                c_max  = form.t.max.data
                c_step = form.t.step.data
                cθ_source_qu = qu.t

                cθv_source = np.arange(c_min, c_max +ε, c_step)
                cθv = hep.mandelstam.t_to_cos_theta(cθv_source, w, q2)

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
                self.qu_index = qu.respfunc_index(quantity)
                self.qu_type = 'respfunc'
            except ValueError:
                self.qu_type = 'amplitude'
                self.qu_index = qu.amplitude_index(quantity)

            # tmp
            # print('SHAPE1', grid_R.shape)
            # print(grid_R)

            self.use_maid_units = True

            if self.qu_type == 'respfunc':
                grid_R = np.apply_along_axis(
                    hep.amplitudes.ampl_to_R, 3, grid_R, #  3rd axis of grid_R with amplitudes
                    # np.sum, 3, grid_R,
                )
                grid_R = grid_R[:,:,:,self.qu_index]
            else:
                grid_R = grid_R[:,:,:,self.qu_index]
                # fixme: temporary real part only

                if self.use_maid_units:  # convert units to MAID compatible
                    grid_R *= 1000 * hep.m_pi
                    quantity = copy.deepcopy(quantity)
                    quantity.unit.tex = r'10^3 / m_{\pi^+}'

                grid_R_im = grid_R.imag
                grid_R = grid_R.real

            # print('SHAPE2', grid_R.shape)

            if self.qu_type == 'amplitude':
                trace_name_suffix = ' (Re)'
            else:
                trace_name_suffix = ''

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
                    'name': 'Interpolated{}, Q²={} GeV², W={} GeV'
                        .format(trace_name_suffix, q2, w),
                    'x': cθv_source,
                    'y': grid_R.flatten(),
                    'marker': {
                        'symbol': 'cross-thin-open',
                        'size': 12,
                        'color': 'orange',
                        'line': {
                            'width': 3,
                        },
                    },
                }]
            }

            if self.qu_type == 'amplitude':
                self.plot['data'].append({
                    'mode': 'markers',
                    'type': 'scatter',
                    'name': 'Interpolated (Im), Q²={} GeV², W={} GeV'
                        .format(q2, w),
                    'x': cθv_source,
                    'y': grid_R_im.flatten(),
                    'marker': {
                        'symbol': 'x-thin-open',
                        'size': 8,
                        'color': 'brown',
                        'opacity': 0.5,
                        'line': {
                            'width': 1,
                        },
                    },
                })

            self.context.update(
                # ampl=ampl,
                ampl={
                    'model': model,
                    'model_id': model.id,
                    'channel': channel,
                    'q2': q2,
                    'w': w,
                },
            )

            if 0 and self.qu_type == 'amplitude':
                maid = MAIDData.load_by_kinematics(Q2=q2, W=w, FS=channel.name)
                cos_θ = np.array(list(maid.keys()))
                H = np.array(list(maid.values()))
                H = H[:,self.qu_index]
                # if self.use_maid_units:  # convert units to MAID compatible
                #     H *= 1000 * hep.m_pi
                if form.varset.data == 'theta':
                    cos_θ = np.rad2deg(np.arccos(cos_θ))[::-1]
                    H = H[::-1]
                elif form.varset.data == 't':
                    cos_θ = hep.mandelstam.cos_theta_to_t(
                        cos_θ, w, q2)

                self.plot['data'] += [{
                    'mode': 'markers',
                    'type': 'scatter',
                    'name': 'MAID Re Q²={} GeV², W={} GeV'
                        .format(q2, w),
                    'x': cos_θ,
                    'y': H.real,
                    'marker': {
                        'symbol': 'square-open',
                        'size': 8,
                        'opacity': 1,
                        # 'color': 'blue',
                        'line': {
                            'width': 1,
                        },
                    },
                }, {
                    'mode': 'markers',
                    'type': 'scatter',
                    'name': 'MAID Im Q²={} GeV², W={} GeV'
                        .format(q2, w),
                    'x': cos_θ,
                    'y': H.imag,
                    'marker': {
                        'symbol': 'square-open',
                        'size': 8,
                        'opacity': 0.5,
                        # 'color': 'green',
                        'line': {
                            'width': 1,
                        },
                    },
                }]


class InterpolateFormCompareView(InterpolateFormView):
    def create_plot(self, form):
        super().create_plot(form)
        model = form.model.data
        channel = form.channel.data
        q2 = form.q2.data
        w = form.w.data

        nearest_Q2_lo = q2
        nearest_Q2_hi = q2

        # nearest_Q2_lo, nearest_Q2_hi = get_value_neighbours(q2, model, channel)
        nearest_W_lo,  nearest_W_hi = get_value_neighbours(w, model, channel, Amplitude.w)

        cos_θ_lo_v, resf_lo_v = get_theta_dependence(model, channel,
            q2, nearest_W_lo, self.qu_index, self.qu_type)
        cos_θ_hi_v, resf_hi_v = get_theta_dependence(model, channel,
            q2, nearest_W_hi, self.qu_index, self.qu_type)

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

        if self.use_maid_units and self.qu_type == 'amplitude':
            # convert units to MAID compatible
            resf_lo_v *= 1000 * hep.m_pi
            resf_hi_v *= 1000 * hep.m_pi

        self.plot['data'] += [{
            'mode': 'markers',
            'type': 'scatter',
            'name': 'Nearest Q²={} GeV², W={} GeV'
                .format(nearest_Q2_lo, nearest_W_lo),
            'x': cos_θ_lo_v,
            'y': resf_lo_v,
            'marker': {
                'symbol': 'triangle-down-open',
                'size': 10,
                'opacity': 0.5,
                'color': 'blue',
                'line': {
                    'width': 1,
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
                'symbol': 'triangle-up-open',
                'size': 10,
                'opacity': 0.5,
                'color': 'green',
                'line': {
                    'width': 1,
                },
            },
        }]

        if self.qu_type == 'amplitude':
            maid = MAIDData.load_by_kinematics(
                Q2=q2, W=w, FS=channel.name)
            cos_θ = np.array(list(maid.keys()))
            H = np.array(list(maid.values()))
            H = H[:,self.qu_index]
            if not self.use_maid_units:
                # convert units from MAID-specific to Gev^-1
                H /= 1000 * hep.m_pi
            if form.varset.data == 'theta':
                cos_θ = np.rad2deg(np.arccos(cos_θ))[::-1]
                H = H[::-1]
            elif form.varset.data == 't':
                cos_θ = hep.mandelstam.cos_theta_to_t(
                    cos_θ, w, q2)

            self.plot['data'] += [{
                'mode': 'markers',
                'type': 'scatter',
                'name': 'MAID Re Q²={} GeV², W={} GeV'
                    .format(q2, w),
                'x': cos_θ,
                'y': H.real,
                'marker': {
                    'symbol': 'square-open',
                    'size': 8,
                    'opacity': 1,
                    # 'color': 'blue',
                    'line': {
                        'width': 1,
                    },
                },
            }, {
                'mode': 'markers',
                'type': 'scatter',
                'name': 'MAID Im Q²={} GeV², W={} GeV'
                    .format(q2, w),
                'x': cos_θ,
                'y': H.imag,
                'marker': {
                    'symbol': 'square-open',
                    'size': 8,
                    'opacity': 0.5,
                    # 'color': 'green',
                    'line': {
                        'width': 1,
                    },
                },
            }]


InterpolateFormView.register_url(bp,
    '/interpolate', 'interpolate_form')

InterpolateFormCompareView.register_url(bp,
    '/interpolate_compare', 'interpolate_form_compare')
