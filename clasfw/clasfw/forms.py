from wtforms import Form, validators, widgets, \
    StringField, IntegerField, FloatField, BooleanField, SubmitField, \
    SelectField, SelectMultipleField, RadioField, FormField, HiddenField
from wtforms_alchemy.fields import QuerySelectField, QuerySelectMultipleField
from markupsafe import Markup
from .models import Channel, Quantity, Model
from .blueprint import qu


def sorted_by_pattern(arr, pattern, key=None):
    if key is None:
        key = lambda o: o
    def _keyfunc(o):
        try:
            idx = pattern.index(key(o))
        except ValueError:
            idx = float('Infinity')
        return idx
    return sorted(arr, key=_keyfunc)


def enabled_channels_factory():
    chs = Channel.query.filter_by(
        status=0
    ).order_by(
        Channel.priority.desc()
    )
    # fixme: temporary workaround
    return sorted_by_pattern(chs, [
        'pi+ n',
        'pi0 p',
        'pi- p',
        'pi0 n',
    ], key=lambda o: o.name)


def enabled_quantities_factory():
    return Quantity.query.filter_by(
        status=0
    ).filter(
        Quantity.name.in_(
            qu.strfun_names +
                [q.name for q in qu.amplitudes])
    ).order_by(
        Quantity.priority.desc()
    )


def enabled_models_factory():
    return Model.query.filter_by(
        status=0
    ).order_by(
        Model.priority.desc()
    )


def get_html_plain_field(obj):
    return Markup(obj.html_plain)
def get_html_field(obj):
    # return obj.__html__()
    return Markup(obj.html)
    # return obj


class MinMaxForm(Form):
    min  = FloatField('min')
    step = FloatField('step')
    max  = FloatField('max')


def create_form(session, qu):
    class InterpolateForm(Form):
        quantity = QuerySelectField('Quantity',
            query_factory   = enabled_quantities_factory,
            option_widget   = widgets.RadioInput(),
            widget          = widgets.ListWidget(prefix_label=False),
            # widget          = widgets.TableWidget(),
            get_label       = get_html_field,
            default         = Quantity.query.filter_by(name=qu.strfun_names[0]).one(),
            # default         = qu.strfuns[0],
        )

        channel = QuerySelectField(
            query_factory   = enabled_channels_factory,
            # option_widget   = widgets.CheckboxInput(),
            option_widget   = widgets.RadioInput(),
            widget          = widgets.ListWidget(prefix_label=False),
            get_label       = get_html_field,
            # get_label       = get_html_plain_field,
            # fixme: no database connection yet when class is creating
            # default         = Channel.query.filter_by(name='inclusive').all(),
            # default         = [''],
            # default         = 'pi0 p',
            # default         = Channel.query.filter_by(name='pi0 p').one(),  ##  fixme!
            default         = Channel.query.first(),  ##  fixme!
        )

        model = QuerySelectField('Model',
            [validators.DataRequired()],
            query_factory   = enabled_models_factory,
            option_widget   = widgets.RadioInput(),
            # option_widget   = Select2Widget(),
            widget          = widgets.ListWidget(prefix_label=False),
            # default         =  Model.query.order_by(Model.id.desc()).first(),  ##  fixme!
            default         =  Model.query.order_by(Model.id.desc()).first(),
        )

        # q2      = FormField(MinMaxForm, qu.Q2.html,
        #     widget = widgets.ListWidget(),
        #     default=dict(min=1, max=1, step=0.1))
        # w       = FormField(MinMaxForm, qu.W.html,
        #     widget = widgets.ListWidget(),
        #     default=dict(min=1.5, max=1.5, step=0.1))

        q2      = FloatField(qu.Q2.html,
            [validators.NumberRange(min=0)],
            default=0.5)
        w       = FloatField(qu.W.html,
            [validators.NumberRange(min=0)],
            default=1.5)

        varset  = HiddenField("Kinematic variables set",
            [validators.AnyOf([
                'cos_theta', 'theta', 't'
            ])],
            default="cos_theta")

        cos_theta = FormField(MinMaxForm, qu.cos_theta.html,
            widget = widgets.ListWidget(),
            default=dict(min=-1, max=1, step=0.1))
        theta = FormField(MinMaxForm, qu.theta.html,
            widget = widgets.ListWidget(),
            default=dict(min=0, max=180, step=10))
        t = FormField(MinMaxForm, qu.t.html,
            widget = widgets.ListWidget(),
            default=dict(min=-2, max=0, step=0.1))

        e_beam  = FloatField(qu.Eb.html,
            default=10.6)

        submit      = SubmitField("Interpolate")

    return InterpolateForm
