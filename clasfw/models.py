__all__ = [
    'Amplitude', 'Model', 'Channel',
]

from database import Base, Column, \
        Integer, SmallInteger, String, DateTime, Boolean, Float, \
        Text, LargeBinary, \
        ForeignKey, ForeignKeyConstraint, relationship, \
        backref, deferred, func, desc
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

import re


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
    name           = Column(String, nullable=False, unique=True)
    description    = Column(Text, nullable=False,
        server_default='')

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
    html           = Column(String, default=default_html_value)
    html_plain     = Column(String, default=default_html_value)
    tex            = Column(String)

    def _repr_html_(self):  # for display_html() function in IPython
        return str(self.html)

    # for use in Markup class and html templates
    # can use {{ value }} instead of {{ value.html|safe }}
    def __html__(self):
        return self.html


class Model(DictionaryMixin, Base):
    author         = Column(String, nullable=False,
        default='')
    comment        = Column(Text, nullable=False,
        default='')



class Channel(DatesMixin, ExtDictionaryMixin, Base):
    pass


def complex_none(r, i):
    return complex(r, i) if r is not None and i is not None else None

class Amplitude(Base):
    __tablename__  = 'amplitudes'
    id             = Column(Integer, primary_key=True, autoincrement=True)
    channel_id     = Column(Integer, ForeignKey(Channel.id))
    channel        = relationship(Channel)
    model_id       = Column(Integer, ForeignKey(Model.id))
    model          = relationship(Model,  # ManyToOne
        # backref=backref('amplitudes', lazy=True, uselist=True) )
        backref='amplitudes')
    q2             = Column(Float)
    w              = Column(Float)
    cos_theta      = Column(Float)

    t1r            = Column(Float)
    t1j            = Column(Float)
    t2r            = Column(Float)
    t2j            = Column(Float)
    t3r            = Column(Float)
    t3j            = Column(Float)
    t4r            = Column(Float)
    t4j            = Column(Float)
    t5r            = Column(Float)
    t5j            = Column(Float)
    t6r            = Column(Float)
    t6j            = Column(Float)


    @hybrid_property
    def t1(self):
        return complex(self.t1r, self.t1j)

    @t1.setter
    def t1(self, value):
        self.t1r = value.real
        self.t1j = value.imag

    @hybrid_property
    def t2(self):
        return complex_none(self.t2r, self.t2j)

    @t2.setter
    def t2(self, value):
        self.t2r = value.real
        self.t2j = value.imag

    @hybrid_property
    def t3(self):
        return complex_none(self.t3r, self.t3j)

    @t3.setter
    def t3(self, value):
        self.t3r = value.real
        self.t3j = value.imag

    @hybrid_property
    def t4(self):
        return complex_none(self.t4r, self.t4j)

    @t4.setter
    def t4(self, value):
        self.t4r = value.real
        self.t4j = value.imag

    @hybrid_property
    def t5(self):
        return complex_none(self.t5r, self.t5j)

    @t5.setter
    def t5(self, value):
        self.t5r = value.real
        self.t5j = value.imag

    @hybrid_property
    def t6(self):
        return complex_none(self.t6r, self.t6j)

    @t6.setter
    def t6(self, value):
        self.t6r = value.real
        self.t6j = value.imag


if __name__ == '__main__':
    import sys, sqlalchemy
    print("Python version: " + sys.version)
    print("SQLAlchemy version: " + sqlalchemy.__version__)
    print("\nTables defined:\n\n" + "\n".join(Base.metadata.tables.keys()))
