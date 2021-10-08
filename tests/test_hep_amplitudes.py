"""HEP amplitudes calculation unit tests."""
import pytest

import numpy as np
from numpy.testing import assert_allclose

import hep
import hep.amplitudes

##  Data source:
##    https://maid.kph.uni-mainz.de/maid2007/maid2007.html


class TestAmplitudes:

    def test_amplitudes(self):

        channel = 'pi0 p'
        Q2 = 1.0       #  GeV**2
        W  = 1.232     #  GeV
        theta_deg = 30 #  deg
        E_beam = 10.6  #  GeV

        # https://maid.kph.uni-mainz.de/cgi-bin/maid1?switch=213&param2=1&param3=3&param50=3&value35=1&value36=1232&value37=0&value41=10&value42=180&param99=0&param11=1&param12=1&param13=1&param14=1&param15=1&param16=1&param17=1&param18=1&param19=1&param20=1&param21=1&param22=1&param23=1&param24=1&param25=1&param26=1&value11=1.0&value12=1.0&value13=1.0&value51=1.0&value52=1.0&value53=1.0&value54=1.0&value55=1.0&value56=1.0&value57=1.0&value58=1.0&value59=1.0&value60=1.0&value61=1.0&value62=1.0&value63=1.0&value64=1.0&value65=1.0&value66=1.0&value67=1.0&value68=1.0&value69=1.0&value70=1.0&value71=1.0&value72=1.0&value73=1.0&value74=1.0&value75=1.0&value76=1.0&value77=1.0&value78=1.0&value79=1.0&value80=1.0&value81=1.0&value82=1.0&value83=1.0&value84=1.0

        #  H values from MAID website
        H = np.array([
            -1.150 +13.910j,
            -8.948 -14.320j,
              .238 - 3.728j,
              .539 + 8.345j,
            - .039 +  .316j,
            - .189 -  .252j
        ])

        # convert units since on MAID site H units are in 10^-3/m_pi+
        H = H / 1000 / hep.m_pi
        H[4:6] *= hep.amplitudes.H56_maid_correction_factor(W, Q2)

        # https://maid.kph.uni-mainz.de/cgi-bin/maid1?switch=211&param2=1&param50=3&value35=1&value36=1232&value37=0&value41=10&value42=180&param99=0&param11=1&param12=1&param13=1&param14=1&param15=1&param16=1&param17=1&param18=1&param19=1&param20=1&param21=1&param22=1&param23=1&param24=1&param25=1&param26=1&value11=1.0&value12=1.0&value13=1.0&value51=1.0&value52=1.0&value53=1.0&value54=1.0&value55=1.0&value56=1.0&value57=1.0&value58=1.0&value59=1.0&value60=1.0&value61=1.0&value62=1.0&value63=1.0&value64=1.0&value65=1.0&value66=1.0&value67=1.0&value68=1.0&value69=1.0&value70=1.0&value71=1.0&value72=1.0&value73=1.0&value74=1.0&value75=1.0&value76=1.0&value77=1.0&value78=1.0&value79=1.0&value80=1.0&value81=1.0&value82=1.0&value83=1.0&value84=1.0

        #  dsigma values from MAID website
        dsigmas_maid = np.array([
            4.9956,    .1637,  -1.1377,   -.6819,    .1303])
        
        # https://maid.kph.uni-mainz.de/cgi-bin/maid1?switch=216&param2=1&param3=1&param4=1&param5=1&param6=1&param7=1&param8=1&param31=2&param50=3&value35=1&value36=1232&value37=0&value41=10&value42=180&param99=0&param11=1&param12=1&param13=1&param14=1&param15=1&param16=1&param17=1&param18=1&param19=1&param20=1&param21=1&param22=1&param23=1&param24=1&param25=1&param26=1&value11=1.0&value12=1.0&value13=1.0&value51=1.0&value52=1.0&value53=1.0&value54=1.0&value55=1.0&value56=1.0&value57=1.0&value58=1.0&value59=1.0&value60=1.0&value61=1.0&value62=1.0&value63=1.0&value64=1.0&value65=1.0&value66=1.0&value67=1.0&value68=1.0&value69=1.0&value70=1.0&value71=1.0&value72=1.0&value73=1.0&value74=1.0&value75=1.0&value76=1.0&value77=1.0&value78=1.0&value79=1.0&value80=1.0&value81=1.0&value82=1.0&value83=1.0&value84=1.0

        #  R values from MAID website
        R_maid = np.array([
            5.635,  .004,  .113,  -1.283,  -.022])

        R = hep.amplitudes.ampl_to_R(H)

        #  TODO!
        #assert_allclose(R, R_maid, rtol=0.02)

        dsigmas = R * hep.amplitudes.R_to_dsigma_factor(W, Q2)

        #print('DS calc: ', dsigmas)
        #print('DS MAID: ', dsigmas_maid)

        assert_allclose(dsigmas, dsigmas_maid, rtol=0.02)
