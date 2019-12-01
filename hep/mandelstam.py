import numpy as np
from .hep import M_p, m_pi, m_pi0


def cos_theta_to_t(cos_theta, W, Q2):
    M_N = M_p
    # m_pi = m_pi

    E_γ_cm = \
        ( W*W - Q2 - M_N**2)       /\
              ( 2*W )

    E_π_cm = \
        ( W*W + m_pi**2 - M_N**2)  /\
              ( 2*W )

    p_γ_cm = np.sqrt(Q2 + E_γ_cm**2)
    p_π_cm = np.sqrt(E_π_cm**2 - m_pi**2)

    t = m_pi**2 - Q2          \
      - 2 * E_π_cm * E_γ_cm   \
      + 2 * p_π_cm * p_γ_cm * cos_theta

    return t


def t_to_cos_theta(t, W, Q2):
    M_N = M_p
    # m_pi = m_pi

    E_γ_cm = \
        ( W*W - Q2 - M_N**2)       /\
              ( 2*W )

    E_π_cm = \
        ( W*W + m_pi**2 - M_N**2)  /\
              ( 2*W )

    p_γ_cm = np.sqrt(Q2 + E_γ_cm**2)
    p_π_cm = np.sqrt(E_π_cm**2 - m_pi**2)

    cos_theta = \
        ( t - m_pi**2 + Q2 + 2 * E_π_cm * E_γ_cm )   /\
                ( 2 * p_π_cm * p_γ_cm )

    return cos_theta
