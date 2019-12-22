__all__ = [
    'Amplitude', 'Model', 'Channel', 'Quantity', 'Unit'
]

from database import Base, Column, \
        Integer, SmallInteger, String, DateTime, Boolean, Float, \
        Text, LargeBinary, \
        ForeignKey, ForeignKeyConstraint, UniqueConstraint, \
        relationship, backref, deferred, func, desc
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from flask import Markup

from .base_models import StatusMixin, DatesMixin, DictionaryMixin, ExtDictionaryMixin


class Channel(DatesMixin, ExtDictionaryMixin, Base):
    pass


class Unit(DatesMixin, ExtDictionaryMixin, Base):
    __tablename__  = 'units'


class Quantity(DatesMixin, ExtDictionaryMixin, Base):
    __tablename__  = 'quantities'
    unit_id        = Column(Integer, ForeignKey(Unit.id))
    # fixme: lazy loading of units causes DetachedInstanceError
    #   <Quantity> is not bound to a Session; lazy load operation of attribute 'unit' cannot proceed
    # after long application uptime
    # for preliminary loaded quantities in before_first_request likq 'qu' object
    unit           = relationship(Unit, lazy='immediate')

    def with_unit(self, unit=None, type='html'):
        # fixme: do not use plain unit ID for comparison!!
        if type=='text':
            type = 'name'
        q = getattr(self, type)

        if self.unit_id not in (0, 1, None) \
        or unit is not None:
            if unit is not None:
                try:
                    u = getattr(unit, type)
                except AttributeError:
                    u = str(unit)
            else:
                u = getattr(self.unit, type)
            fmt = {
                'html': r'{0}, <span class="unit">{1}</span>',
                'tex':  r"{0}, \, \mathrm{{{1}}}",
            }.get(type, "{0}, {1}")
            q = fmt.format(q, u)
        if type == 'html':
            q = '<span class="math">{}</span>'.format(q)
            q = Markup(q)
        return q

    @property
    def wu(self):
        return self.with_unit()

    @property
    def wu_tex(self):
        return self.with_unit(type='tex')

    def __html__(self):
        return '<span class="math">{}</span>'.format(self.html)


class Model(DatesMixin, DictionaryMixin, Base):
    author         = Column(String(255), nullable=False,
        default='')
    comment        = Column(Text, nullable=False,
        default='')


def complex_or_none(r, i):
    if r is None and i is None:
        return None
    return complex(r, i)


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

    number = 6

    H1r            = Column(Float)
    H1j            = Column(Float)
    H2r            = Column(Float)
    H2j            = Column(Float)
    H3r            = Column(Float)
    H3j            = Column(Float)
    H4r            = Column(Float)
    H4j            = Column(Float)
    H5r            = Column(Float)
    H5j            = Column(Float)
    H6r            = Column(Float)
    H6j            = Column(Float)

    @hybrid_property
    def H1(self):
        return complex_or_none(self.H1r, self.H1j)

    @H1.setter
    def H1(self, value):
        self.H1r = value.real
        self.H1j = value.imag

    @hybrid_property
    def H2(self):
        return complex_or_none(self.H2r, self.H2j)

    @H2.setter
    def H2(self, value):
        self.H2r = value.real
        self.H2j = value.imag

    @hybrid_property
    def H3(self):
        return complex_or_none(self.H3r, self.H3j)

    @H3.setter
    def H3(self, value):
        self.H3r = value.real
        self.H3j = value.imag

    @hybrid_property
    def H4(self):
        return complex_or_none(self.H4r, self.H4j)

    @H4.setter
    def H4(self, value):
        self.H4r = value.real
        self.H4j = value.imag

    @hybrid_property
    def H5(self):
        return complex_or_none(self.H5r, self.H5j)

    @H5.setter
    def H5(self, value):
        self.H5r = value.real
        self.H5j = value.imag

    @hybrid_property
    def H6(self):
        return complex_or_none(self.H6r, self.H6j)

    @H6.setter
    def H6(self, value):
        self.H6r = value.real
        self.H6j = value.imag

    @hybrid_property
    def H(self):
        return self.H1, self.H2, self.H3, self.H4, self.H5, self.H6

    @H.setter
    def H(self, value):
        self.H1, self.H2, self.H3, self.H4, self.H5, self.H6 = value


    __table_args__ = (
        UniqueConstraint(
            channel_id, model_id,
            q2, w, cos_theta,
            name='grid',
        ),
    {} )


if __name__ == '__main__':
    import sys, sqlalchemy
    print("Python version: " + sys.version)
    print("SQLAlchemy version: " + sqlalchemy.__version__)
    print("\nTables defined:\n\n" + "\n".join(Base.metadata.tables.keys()))
