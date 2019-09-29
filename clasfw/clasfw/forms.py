from flask_wtf import FlaskForm
# from wtforms.validators import DataRequired
from wtforms import Form, StringField, IntegerField, \
                    SelectField, SelectMultipleField, RadioField, \
                    FloatField, BooleanField, SubmitField, \
                    FormField, validators, widgets
from wtforms_alchemy.fields import QuerySelectField, QuerySelectMultipleField
from markupsafe import Markup
from .models import Channel, Quantity, Model
from .blueprint import qu



class CheckBoxSetField(SelectMultipleField):
    """
    Like a SelectMultipleField, except displays a list of checkboxes.

    Iterating the field will produce subfields (each containing a label as
    well) in order to allow custom rendering of the individual checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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
        Quantity.name.in_([
            "dsigma/dOmega",
            "dsigma_T/dOmega",
            "dsigma_L/dOmega",
            "dsigma_TT/dOmega",
            "dsigma_TL/dOmega",
            "dsigma_TL'/dOmega",
        ])
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
    return Markup(obj.html)
    # return obj


class MinMaxForm(Form):
    min  = FloatField('min')
    step = FloatField('step')
    max  = FloatField('max')


def create_form(session, qu):
    class InterpolateForm(Form):
        # quantity = RadioField('Quantity',
        #     default='dsigma/dOmega',
        #     choices=enabled_quantities_factory
        # ,)
        quantity = QuerySelectField('Quantity',
            query_factory   = enabled_quantities_factory,
            default         = 'dsigma/dOmega',
            get_label       = get_html_field,
        )

        channels = QuerySelectMultipleField(
            query_factory   = enabled_channels_factory,
            option_widget   = widgets.CheckboxInput(),
            widget          = widgets.ListWidget(prefix_label=False),
            get_label       = get_html_field,
            # get_label       = get_html_plain_field,
            # fixme: no database connection yet when class is creating
            # default         = Channel.query.filter_by(name='inclusive').all(),
            # default         = [''],
        )

        model = QuerySelectMultipleField('Model',
            query_factory   = enabled_models_factory,
            option_widget   = widgets.CheckboxInput(),
            widget          = widgets.ListWidget(prefix_label=False),
            # coerce=int,
        )

        q2      = FormField(MinMaxForm, qu.Q2.html,
            default=dict(min=2, max=2, step=0.1))
        w       = FormField(MinMaxForm, qu.W.html,
            default=dict(min=2, max=2, step=0.1))
        cos_theta = FormField(MinMaxForm, qu.cos_theta.html,
            default=dict(min=-1, max=1, step=0.1))
        e_beam  = FloatField(qu.Eb.html,
            default=10.6)

        submit      = SubmitField("Interpolate")

    return InterpolateForm
