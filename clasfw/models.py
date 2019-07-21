__all__ = [
    'Amplitude', 'Model', 'Channel', 'Quantity'
]

from database import Base, Column, \
        Integer, SmallInteger, String, DateTime, Boolean, Float, \
        Text, LargeBinary, \
        ForeignKey, ForeignKeyConstraint, UniqueConstraint, \
        relationship, backref, deferred, func, desc
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


class Quantity(DatesMixin, ExtDictionaryMixin, Base):
    __tablename__  = 'quantities' 


def complex_none(r, i):
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

    number = 12

    a0r            = Column(Float)
    a0j            = Column(Float)
    a1r            = Column(Float)
    a1j            = Column(Float)
    a2r            = Column(Float)
    a2j            = Column(Float)
    a3r            = Column(Float)
    a3j            = Column(Float)
    a4r            = Column(Float)
    a4j            = Column(Float)
    a5r            = Column(Float)
    a5j            = Column(Float)
    a6r            = Column(Float)
    a6j            = Column(Float)
    a7r            = Column(Float)
    a7j            = Column(Float)
    a8r            = Column(Float)
    a8j            = Column(Float)
    a8r            = Column(Float)
    a8j            = Column(Float)
    a9r            = Column(Float)
    a9j            = Column(Float)
    a10r           = Column(Float)
    a10j           = Column(Float)
    a11r           = Column(Float)
    a11j           = Column(Float)

    sigma_t        = Column(Float)
    sigma_l        = Column(Float)
    sigma_tt       = Column(Float)
    sigma_tl       = Column(Float)
    sigma_tlp      = Column(Float)

    @hybrid_property
    def a0(self):
        return complex_none(self.a0r, self.a0j)

    @a0.setter
    def a0(self, value):
        self.a0r = value.real
        self.a0j = value.imag

    @hybrid_property
    def a1(self):
        return complex_none(self.a1r, self.a1j)

    @a1.setter
    def a1(self, value):
        self.a1r = value.real
        self.a1j = value.imag

    @hybrid_property
    def a2(self):
        return complex_none(self.a2r, self.a2j)

    @a2.setter
    def a2(self, value):
        self.a2r = value.real
        self.a2j = value.imag

    @hybrid_property
    def a3(self):
        return complex_none(self.a3r, self.a3j)

    @a3.setter
    def a3(self, value):
        self.a3r = value.real
        self.a3j = value.imag

    @hybrid_property
    def a4(self):
        return complex_none(self.a4r, self.a4j)

    @a4.setter
    def a4(self, value):
        self.a4r = value.real
        self.a4j = value.imag

    @hybrid_property
    def a5(self):
        return complex_none(self.a5r, self.a5j)

    @a5.setter
    def a5(self, value):
        self.a5r = value.real
        self.a5j = value.imag

    @hybrid_property
    def a6(self):
        return complex_none(self.a6r, self.a6j)

    @a6.setter
    def a6(self, value):
        self.a6r = value.real
        self.a6j = value.imag

    @hybrid_property
    def a7(self):
        return complex_none(self.a7r, self.a7j)

    @a7.setter
    def a7(self, value):
        self.a7r = value.real
        self.a7j = value.imag

    @hybrid_property
    def a8(self):
        return complex_none(self.a8r, self.a8j)

    @a8.setter
    def a8(self, value):
        self.a8r = value.real
        self.a8j = value.imag

    @hybrid_property
    def a9(self):
        return complex_none(self.a9r, self.a9j)

    @a9.setter
    def a9(self, value):
        self.a9r = value.real
        self.a9j = value.imag

    @hybrid_property
    def a10(self):
        return complex_none(self.a10r, self.a10j)

    @a10.setter
    def a10(self, value):
        self.a10r = value.real
        self.a10j = value.imag

    @hybrid_property
    def a10(self):
        return complex_none(self.a10r, self.a10j)

    @a10.setter
    def a10(self, value):
        self.a10r = value.real
        self.a10j = value.imag

    @hybrid_property
    def a11(self):
        return complex_none(self.a11r, self.a11j)

    @a11.setter
    def a11(self, value):
        self.a11r = value.real
        self.a11j = value.imag

    @hybrid_property
    def a(self):
        return self.a0, self.a1, self.a2, self.a3, self.a4, self.a5, \
               self.a6, self.a7, self.a8, self.a9, self.a10, self.a11

    @a.setter
    def a(self, value):
        self.a0, self.a1, self.a2, self.a3, self.a4, self.a5, \
        self.a6, self.a7, self.a8, self.a9, self.a10, self.a11 = value

    @hybrid_property
    def strfuns(self):
        return self.sigma_t, self.sigma_l, self.sigma_tt, self.sigma_tl, self.sigma_tlp

    _lambdas_by_index = []
    _index_by_lambdas = {}
    @classmethod
    def _init_lambdas(cls):
        i=0
        for lambda_B in -2, +2:
            for lambda_g in -1, 0, +1:
                for lambda_p in -2, +2:
                    lambdas = lambda_B, lambda_g, lambda_p
                    cls._lambdas_by_index.append(lambdas)
                    cls._index_by_lambdas[lambdas] = i
                    i += 1
    # _init_lambdas()
    @classmethod
    def lambdas_int_by_aindex(cls, a_index):
        return cls._lambdas_by_index[a_index]

    @staticmethod
    def lambda_int_to_str(l):
        return {
            -2: "−½",
            +2: "+½",
            +1: "+1",
            -1: "−1",
        }.get(l, str(l))

    @classmethod
    def a_index_by_lambdas_int(lb, lp, lg):
        """
        Returns list index in a array field
        for 1/lambda_B, 1/lambda_p, 1/lambda_gamma specified
        """
        return cls._index_by_lambdas[lb, lp, lg]


    def by_int_lambdas(self, lb, lg, lp):
        return self.a[
            self.a_index_by_lambdas_int(lb=lb, lg=lg, lp=lp)
        ]

    __table_args__ = ( 
        UniqueConstraint(
            channel_id, model_id, q2, w, cos_theta,
            name='grid',
        ),
    {} )


Amplitude._init_lambdas()


def sum_lplb(A, lg1, lg2=None):
    if lg2 is None:
        lg2 = lg1
    s = 0
    for lp in -2, +2:
        for lb in -2, +2:
            i1 = Amplitude.a_index_by_lambdas_int(lb, lp, lg1)
            i2 = Amplitude.a_index_by_lambdas_int(lb, lp, lg2)
            s += A[i1].conjugate()*A[i2]
    return s


def ampl_to_sigma_T(A):
    M_plu2 = sum_lplb(A, +1)
    M_min2 = sum_lplb(A, -1)
    return M_plu2 + M_min2


def ampl_to_sigma_L(A):
    M_0_2 = sum_lplb(A, 0)
    return M_0_2


def ampl_to_sigma_TT(A, eps_T):
    M_min_conj_M_plu = sum_lplb(A, -1, +1)
    return -2*eps_T*M_min_conj_M_plu.real


def sum_ampl_M0MpMm(A):
    """
    $$ M_0^* ( M_{+} - M_{-} ) $$
    """
    s = 0
    # fixme: avoid "magic" constants +2/-2
    for lp in -2, +2:
        for lb in -2, +2:
            i1, i2, i3 = (
                Amplitude.a_index_by_lambdas_int(lb, lp, lg)
                    for lg in (0, +1, -1))
            s += A[i1].conjugate() * (
                A[i2] - A[i3].conjugate())
    return s


def ampl_to_sigma_TL_TLP(a, eps_T):
    M0MpMm = sum_ampl_M0MpMm(a)
    return \
        -2*np.sqrt(eps_T*(1+eps_T))*M0MpMm.real,  \
         2*np.sqrt(eps_T*(1-eps_T))*M0MpMm.imag


def strfuns_to_dsigma(W, Q2, Eb, phi, st, sl, stt, stl, stlp):
    alpha = 1/137
    M_p = 0.938 ## GeV
    # fixme: use correct mass for pi^0 instead of pi^+- for pi0p reaction
    m_m = 0.13957018 ## GeV ; 0.1349766 for pi^0
    M_N = M_p
    M_B = M_N ## fixme: ???
    K_L = (W*W - M_N*M_N) / (2*M_N)
    E_m = (W*W + m_m*m_m - M_B*M_B)
    p_m = np.sqrt(E_m*E_m - m_m*m_m)
    h = +1 ## -1 ???
    eps_T = eps_T(W, Q2, Eb) ## ???

    sin_theta = np.sin(theta) ## ???

    ds = st + 2*eps_T*sl +  \
         eps_T*np.cos(2*phi)*stt +  \
         np.sqrt(eps_T*(1+eps_T))*np.cos(phi)*stl +  \
         np.sqrt(eps_T*(1-eps_T))*np.sin(phi)*stlp*h
    ds *= alpha*p_m / (32 * np.pi * K_L * M_N * W) * sin_theta
    return ds


if __name__ == '__main__':
    import sys, sqlalchemy
    print("Python version: " + sys.version)
    print("SQLAlchemy version: " + sqlalchemy.__version__)
    print("\nTables defined:\n\n" + "\n".join(Base.metadata.tables.keys()))
