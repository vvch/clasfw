import numpy as np

alpha   = 1.0 / 137.035999139     #  Fine-structure constant
M_p     = 0.9382720813            #  [GeV]
M_p2    = M_p**2                  #  [GeV**2]
GeVm2_per_mcbn = 2.57E-3          #  [Gev^2/mcbn], conversion factor from mcbn to GeV

α4π2 = 4*np.pi*np.pi*alpha


def W2nu(W, Q2):
    return \
    ( W*W - M_p2 + Q2 )   /\
          ( 2*M_p )


def nu2xB(nu, Q2):
    return \
          Q2        /\
    ( 2* M_p*nu )


def xB2nu(xB, Q2):
    return   Q2       \
      / ( 2*xB*M_p )


def xB2W(xB, Q2):
    # try:
        return np.sqrt( Q2/xB - Q2 + M_p2 )
    # except ZeroDivisionError as e:
    #     # fixme: temporary, make more sensible message
    #     raise ValueError(
    #         "Can't calculate W for Q^2={} and xB={}".format(Q2, xB))


def W2xB(W, Q2):
    return nu2xB(W2nu(W, Q2), Q2)


def ε_T(W, Q2, E, ν=None):
    if ν is None:
        ν = W2nu(W, Q2)
    ν2 = ν**2
    sin2θ2 = Q2 / ( 4*(E-ν)*E )
    tg2θ2  = sin2θ2 / (1 - sin2θ2)
    return 1 / (
        1 + 2*(1+ν2/Q2)*tg2θ2 )


def σ_to_F1F2(σ, Q2, E, R, W=None, v=None):
    σ *= GeVm2_per_mcbn
    if ν is None:
        ν = W2nu(W, Q2)
    ν2 = ν*ν
    ε = ε_T(W, Q2, E, ν=ν)  #  W is spare
    σT = σ    \
      / ( 1 + R*ε )
    σL = R*σT
    W_2 = (σL+σT) * (2*ν*M_p - Q2)*(-Q2)  \
        / (α4π2   * 2* M_p*(-Q2-ν2))
    k = (2* M_p*ν - Q2) \
      / (2* M_p       )
    W_1 = k * σT  \
        / α4π2
    F1 = W_1 * M_p
    F2 = W_2 * ν
    return (F1, F2)


def SigTL_from_Q2nuEF1F2(Q2, nu, E, F1, F2):
    ν2 = nu*nu
    k  = ( 2*M_p*nu - Q2 ) \
       / ( 2*M_p           )
    k1 = M_p*k  \
       / α4π2
    k2 = ( nu* k * (-Q2)  ) \
       / ( α4π2* (-Q2-ν2) )
    sigmaT = F1 / k1
    sigmaL = F2 / k2 - sigmaT

    return (sigmaT / GeVm2_per_mcbn, sigmaL / GeVm2_per_mcbn)


def SigTot_from_Q2nuESigTL(Q2, nu, E, sigmaT, sigmaL):
    eps = ε_T(None, Q2, E, ν=nu)
    return sigmaT + eps*sigmaL


def SigTot_from_Q2nuEF1F2(Q2, nu, E, F1, F2):
    return SigTot_from_Q2nuESigTL(
        Q2, nu, E,
        *SigTL_from_Q2nuEF1F2(Q2, nu, E, F1, F2))

def F2_to_F1(F2, R, xB, Q2):
    ν = xB2nu(xB, Q2)
    ν2 = ν*ν
    mult = M_p / ( ν * (1+R) ) * (Q2+ν2) / Q2
    return mult * F2


def F2_to_Sig(xB, F2, Q2, E, R):
    ν = xB2nu(xB, Q2)
    F1 = F2_to_F1(F2, R, xB, Q2)
    return SigTot_from_Q2nuEF1F2(Q2, ν, E, F1, F2)
