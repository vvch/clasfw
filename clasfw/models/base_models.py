__all__ = [
    'StatusMixin', 'DatesMixin', 'DictionaryMixin', 'ExtDictionaryMixin'
]

from database import Base, Column, \
        Integer, SmallInteger, String, DateTime, \
        Text, LargeBinary, \
        relationship, backref, deferred, func, desc
from sqlalchemy.ext.declarative import declared_attr


class StatusMixin:
    id             = Column(Integer, primary_key=True, autoincrement=True)
    status         = Column(Integer, default=0)


class DatesMixin:
    mdate = Column(DateTime, nullable=False,
        default=func.now(), server_default=func.now(),
        onupdate=func.now(), server_onupdate=func.now())
    cdate = Column(DateTime, nullable=False,
        default=func.now(), server_default=func.now())
    # mdate          = Column(DateTime, onupdate=func.utc_timestamp())


class DictionaryMixin(StatusMixin):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    priority       = Column(Integer, autoincrement=True)
    name           = Column(String(255), nullable=False, unique=True)
    description    = Column(Text)

    # __mapper_args__ = {
    #     'order_by': 'priority desc'
    # }

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.name)

    def __str__(self):
        # str() to prevent exception when name is NULL, e. g.
        return str(self.name)


def default_html_value(context):
    # return context.current_parameters['name']
    if not context:  # creating new object via admin form
        return
    # return context.current_parameters['text']
    return context.current_parameters['name']
    # return context.current_parameters[
    #     DictionaryMixin.name.
    # ]


class ExtDictionaryMixin(DictionaryMixin):
    html           = Column(String(255), default=default_html_value)
    html_plain     = Column(String(255), default=default_html_value)
    tex            = Column(String(255))

    def _repr_html_(self):  # for display_html() function in IPython
        return str(self.html)

    # for use in Markup class and html templates
    # can use {{ value }} instead of {{ value.html|safe }}
    def __html__(self):
        return self.html
