import numpy as np
from numpy import sqrt, sin, cos
from .hep import mcb_per_GeVm2, alpha, M_p, M_p2, m_pi, m_pi0


"""
Formalism source:
arXiv:nucl-th/9506029
DOI:10.1007/BF01289506
    G. Knöchlein, D. Drechsel, L. Tiator
    Photo- and Electroproduction of Eta Mesons
    Z.Phys.A352:327-343,1995
    p. 19. Appendix D.

https://maid.kph.uni-mainz.de/maid2007/maid2007.html
"""


strfun_indexes = "T  L  TT  TL  TL'".split()


#  "-1" in H indexes down here since H array indexes starts from 0

def ampl_to_R_T_00(H):
    return (
        np.abs(H[1-1])**2 +
        np.abs(H[2-1])**2 +
        np.abs(H[3-1])**2 +
        np.abs(H[4-1])**2
    ) / 2


def ampl_to_R_L_00(H):
    return (
        np.abs(H[5-1])**2 +
        np.abs(H[6-1])**2
    )


def ampl_to_R_TL_00(H):
    return (
        + H[5-1].conjugate() * H[1-1]
        - H[5-1].conjugate() * H[4-1]
        + H[6-1].conjugate() * H[2-1]
        + H[6-1].conjugate() * H[3-1]
    ).real / np.sqrt(2)


def ampl_to_R_TT_00(H):
    return (
        - H[1-1].conjugate() * H[4-1]
        + H[2-1].conjugate() * H[3-1]
    ).real


def ampl_to_R_TLp_00(H):
    return (
        - H[5-1].conjugate() * H[1-1]
        + H[5-1].conjugate() * H[4-1]
        - H[6-1].conjugate() * H[2-1]
        - H[6-1].conjugate() * H[3-1]
    ).imag / np.sqrt(2)


def ampl_to_R(H):
    """Results in mcb/sr, amplitudes in GeV^-1"""
    return np.array([
        ampl_to_R_T_00(H),
        ampl_to_R_L_00(H),
        ampl_to_R_TT_00(H),
        ampl_to_R_TL_00(H),
        ampl_to_R_TLp_00(H),
    ]) * mcb_per_GeVm2


def H56_maid_correction_factor(W, Q2):
    """
    Correction factor to multiply H5 and H6 helicity amplitudes
    in order to avoid zero division uncertainty
    """
    omega_gamma = (W*W - Q2 - M_p2)  \
                / (2 * W)
    return np.sqrt(Q2) / omega_gamma


def R_to_dsigma_factor(W, Q2):
    """
    dsigma_v [mcb/sr] = R_v [mcb/sr] * response_funcs_to_dsigmas(Q2, W)
    """
    # fixme: use correct mass for pi^0 instead of pi^+- for pi0p reaction
    #  m_m and M_B stand for meson and baryon masses
    m_m = m_pi  ## or m_pi0 for pi0p final state
    M_B = M_p
    #  E_m stands for meson energy in c. m.
    E_m = (W*W + m_m*m_m - M_B*M_B) / (2*W)
    #  p_m is absolute value of meson three-momentum
    p_m = sqrt(E_m*E_m - m_m*m_m)

    k_γ_cm = (W**2 - M_B**2) / (2*W)

    return p_m / k_γ_cm


def R_to_dsigma(W, Q2, eps_T, phi, h, response_funcs):
    """
    Calculate differential cross-section
    from response functions
    for specified kinematics
    """

    dσ_T, dσ_L, dσ_TT, dσ_TL, dσ_TLp = response_funcs * R_to_dsigma_factor(W, Q2)

    ## ε is virtual photon polarization parameter
    ε = eps_T
    εL = ε
    # not using ε_L on the contrary to Drechsel's article

    ds = dσ_T                                        \
       + dσ_L   * εL                                 \
       + dσ_TL  * sqrt(2*εL*(1+ε)) * cos(phi)        \
       + dσ_TT  * ε                * cos(2*phi)      \
       + dσ_TLp * sqrt(2*εL*(1-ε)) * sin(phi)   * h

    return ds


def H_to_dsigma(W, Q2, eps_T, phi, h, H):
    return R_to_dsigma(
        W, Q2, eps_T, phi, h,
        ampl_to_R(H) )
