import numpy as np
from .hep import mcb_per_GeVm2, alpha, M_p


_lambdas_by_index = []
_index_by_lambdas = {}

ampl_num = 12
rlambda_all_B = -2, +2
rlambda_all_g = -1, 0, +1
rlambda_all_p = -2, +2


def _init_lambdas():
    i=0
    for lambda_B in rlambda_all_B:
        for lambda_g in rlambda_all_g:
            for lambda_p in rlambda_all_p:
                # lambdas = lambda_B, lambda_g, lambda_p
                lambdas = lambda_B, lambda_p, lambda_g
                _lambdas_by_index.append(lambdas)
                _index_by_lambdas[lambdas] = i
                i += 1
_init_lambdas()


def rlambdas_by_aindex(a_index):
    return _lambdas_by_index[a_index]


def rlambda_to_str(l):
    return {
        -2: "−½",
        +2: "+½",
        +1: "+1",
        -1: "−1",
    }.get(l, str(l))


def aindex_by_rlambdas(lb, lp, lg):
    """
    Returns list index in a array field
    for 1/lambda_B, 1/lambda_p, 1/lambda_gamma specified
    """
    return _index_by_lambdas[lb, lp, lg]


def sum_lplb(A, lg1, lg2=None):
    if lg2 is None:
        lg2 = lg1
    s = 0
    for lp in rlambda_all_p:
        for lb in rlambda_all_B:
            i1 = aindex_by_rlambdas(lb, lp, lg1)
            i2 = aindex_by_rlambdas(lb, lp, lg2)
            s += A[i1].conjugate()*A[i2]
    return s


def ampl_to_sigma_T(A):
    M_plu2 = sum_lplb(A, +1)
    M_min2 = sum_lplb(A, -1)
    sT = M_plu2 + M_min2
    if sT.imag != 0:
        raise RuntimeError(
            "Non-zero imaginary part for sigma_T at A={}".format(A))
    return sT.real
    # return M_plu2 + M_min2


def ampl_to_sigma_L(A):
    M_0_2 = sum_lplb(A, 0)
    if M_0_2.imag != 0:
        raise RuntimeError(
            "Non-zero imaginary part for sigma_L at A={}".format(A))
    return M_0_2.real
    # return M_0_2


def ampl_to_sigma_TT(A):
    M_min_conj_M_plu = sum_lplb(A, -1, +1)
    return -2*M_min_conj_M_plu.real


def sum_ampl_M0MpMm(A):
    """
    $$ M_0^* ( M_{+} - M_{-} ) $$
    """
    s = 0
    for lp in rlambda_all_p:
        for lb in rlambda_all_B:
            i1, i2, i3 = (
                aindex_by_rlambdas(lb, lp, lg)
                    for lg in (0, +1, -1))
            s += A[i1].conjugate() * (
                A[i2] - A[i3].conjugate())
    return s


def ampl_to_sigma_TL_TLP(A):
    M0MpMm = sum_ampl_M0MpMm(A)
    return \
        -2*M0MpMm.real,  \
         2*M0MpMm.imag
    # return \
    #     -2*np.sqrt(eps_T*(1+eps_T))*M0MpMm.real,  \
    #      2*np.sqrt(eps_T*(1-eps_T))*M0MpMm.imag


def ampl_to_strfuns(A):
    return (ampl_to_sigma_T(A), ampl_to_sigma_L(A), \
        ampl_to_sigma_TT(A)) + ampl_to_sigma_TL_TLP(A)


def strfuns_to_dsigma(W, Q2, cos_theta, eps_T, phi, st, sl, stt, stl, stlp):
    # fixme: use correct mass for pi^0 instead of pi^+- for pi0p reaction
    m_m = 0.13957018 ## GeV ; 0.1349766 for pi^0
    M_N = M_p
    M_B = M_N ## fixme: ???
    K_L = (W*W - M_N*M_N) / (2*M_N)
    E_m = (W*W + m_m*m_m - M_B*M_B)
    p_m = np.sqrt(E_m*E_m - m_m*m_m)
    
    # fixme: should depend on reaction?
    h = +1 ## -1 ???

    sin_theta = np.sqrt(1-cos_theta**2)

    ds = st + 2*eps_T*sl +  \
         eps_T*np.cos(2*phi)*stt +  \
         np.sqrt(eps_T*(1+eps_T))*np.cos(phi)*stl +  \
         np.sqrt(eps_T*(1-eps_T))*np.sin(phi)*stlp*h
    ds *= alpha*p_m / (4*4*4 * np.pi * K_L * M_N * W) * sin_theta
    return ds * mcb_per_GeVm2
