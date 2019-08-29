__all__ = [
    'StatusMixin', 'DatesMixin', 'DictionaryMixin', 'ExtDictionaryMixin'
]

from database import Base, Column, \
        Integer, SmallInteger, String, TIMESTAMP, \
        Text, LargeBinary, \
        relationship, backref, deferred, func, desc
from sqlalchemy.ext.declarative import declared_attr


class StatusMixin:
    id             = Column(Integer, primary_key=True, autoincrement=True)
    status         = Column(Integer, default=0)

import sqlalchemy
from sqlalchemy import text
class DatesMixin:
    # in MySQL should be first TIMESTAMP column
    mdate = Column(TIMESTAMP, nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        # server_default=text(
        #     "{0} ON UPDATE {0}".format(func.current_timestamp())
        # ),
        server_onupdate=sqlalchemy.schema.FetchedValue(),
    )
        # server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    cdate = Column(TIMESTAMP, nullable=False,
        default=func.now(),
        server_default=func.current_timestamp())
    # mdate          = Column(DateTime, onupdate=func.utc_timestamp())
    # mdate          = Column(DateTime, onupdate=func.current_timestamp())


class DictionaryMixin(StatusMixin):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    priority       = Column(Integer, autoincrement=True)
    name           = Column(String(255), nullable=False, unique=True)
    description    = Column(Text)
    # description    = Column(Text, nullable=False,
    #     server_default='')  ##  in MySQL TEXT field can not have default value

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
