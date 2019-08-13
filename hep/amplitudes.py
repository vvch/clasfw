import numpy as np
from numpy import sqrt, sin, cos
from .hep import mcb_per_GeVm2, alpha, M_p, m_pi, m_pi0


"""
Formalism source:
arXiv:nucl-th/9506029
DOI:10.1007/BF01289506 
    G. Knöchlein, D. Drechsel, L. Tiator
    Photo- and Electroproduction of Eta Mesons
    Z.Phys.A352:327-343,1995
    p. 19. Appendix D.
"""


def ampl_to_R_T_00(H):
    return (
        np.abs(H[1])**2 +
        np.abs(H[2])**2 +
        np.abs(H[3])**2 +
        np.abs(H[4])**2
    ) / 2


def ampl_to_R_L_00(H):
    return (
        np.abs(H[5])**2 +
        np.abs(H[6])**2
    )


def ampl_to_R_TL_00(H):
    return (
        + H[5].conjugate() * H[1]
        - H[5].conjugate() * H[4]
        + H[6].conjugate() * H[2]
        + H[6].conjugate() * H[3]
    ).real / np.sqrt(2)
    #  fixme: take out sqrt(2) ? cf. Mokeev's comment in DT_only.pdf write-up


def ampl_to_R_TT_00(H):
    return (
        - H[1].conjugate() * H[4]
        + H[2].conjugate() * H[3]
    ).real


def ampl_to_R_TLp_00(H):
    return (
        - H[5].conjugate() * H[1]
        + H[5].conjugate() * H[4]
        - H[6].conjugate() * H[2]
        - H[6].conjugate() * H[3]
    ).imag / np.sqrt(2)


def ampl_to_strfuns(H):
    return np.array([
        ampl_to_R_T_00(H),
        ampl_to_R_L_00(H),
        ampl_to_R_TT_00(H),
        ampl_to_R_TL_00(H),
        ampl_to_R_TLp_00(H),
    ])


def strfuns_to_dsigma(W, Q2, cos_theta, eps_T, phi, h, strfuns):
    """
    Calculate differential cross-section
    from structure functions
    for specified kinematics
    """
    # fixme: use correct mass for pi^0 instead of pi^+- for pi0p reaction
    m_m = m_pi  ## or m_pi0 for pi0p final state
    M_N = M_p
    M_B = M_N ## fixme: ???
    # K_L = (W*W - M_N*M_N) / (2*M_N)
    E_m = (W*W + m_m*m_m - M_B*M_B) / (2*W)
    p_m = sqrt(E_m*E_m - m_m*m_m)
    
    R_T, R_L, R_TT, R_TL, R_TLp = strfuns

    E_γ_cm = (W*W - Q2 - M_N) / (2*W)
    K_γ_cm = sqrt(Q2 + E_γ_cm**2)
    sinθ   = sqrt(1-cos_theta**2)

    ε = eps_T
    εL = ε

    ds = R_T                                        \
       + R_L   * εL                                 \
       + R_TL  * sqrt(2*εL*(1+ε)) * cos(phi)        \
       + R_TT  * ε                * cos(2*phi)      \
       + R_TLp * sqrt(2*εL*(1-ε)) * sin(phi)   *h   \
    # equation end

    ds *= p_m / K_γ_cm / (4*4*np.pi) * sinθ
    # ds *= alpha*p_m / (4*4*4 * np.pi * K_L * M_N * W)
    return ds * mcb_per_GeVm2
