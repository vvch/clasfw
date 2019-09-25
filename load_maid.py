from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import re, requests, requests_cache
import numpy as np
from pprint import pprint
from furl import furl

from clasfw.models import Model, Amplitude, Channel
import hep
import hep.amplitudes


class MAIDData(dict):
    url = "https://maid.kph.uni-mainz.de/cgi-bin/maid1?switch=213&param2=1&param3=3&param50=3&value35=1&value36=2000&value37=0&value41=10&value42=180&param99=0&param11=1&param12=1&param13=1&param14=1&param15=1&param16=1&param17=1&param18=1&param19=1&param20=1&param21=1&param22=1&param23=1&param24=1&param25=1&param26=1&value11=1.0&value12=1.0&value13=1.0&value51=1.0&value52=1.0&value53=1.0&value54=1.0&value55=1.0&value56=1.0&value57=1.0&value58=1.0&value59=1.0&value60=1.0&value61=1.0&value62=1.0&value63=1.0&value64=1.0&value65=1.0&value66=1.0&value67=1.0&value68=1.0&value69=1.0&value70=1.0&value71=1.0&value72=1.0&value73=1.0&value74=1.0&value75=1.0&value76=1.0&value77=1.0&value78=1.0&value79=1.0&value80=1.0&value81=1.0&value82=1.0&value83=1.0&value84=1.0"


    def get_kinematics(self, text):
        mo = re.search(r"""
                Q\^2 \s* \= \s* ([\d\.]+) \s* \(GeV\/c\)\^2\;
                \s*
                W \s* \= \s* ([\d\.]+) \s* \(MeV\)
            """,
            text,
            re.M+re.S+re.X)
        Q2, W = mo.group(1, 2)
        # print(Q2, W)
        self.Q2 = float(Q2)
        self.W  = float(W) / 1000  ##  MeV to GeV


    @classmethod
    def parse(cls, text):
        self = cls()
        self.get_kinematics(text)

        matches = re.finditer(r"""
                ^
                \s+\(deg\) .*? \n
                ([\s\d\.\-]*?) \n
                (?: \s* | <.* )
                $
            """,
            text,
            re.M+re.S+re.X)

        t1, t2 = [m.group(1) for m in matches]
        # print(t1, "\n", t2)

        def parse_block(t, out=None):
            if out is None:
                out = {}
            for line in t.split("\n"):
                v = [float(x) for x in line.split()]
                c = np.cos(np.deg2rad(v[0]))
                if np.isclose(c, 0):
                    c = 0
                H1, H2, H3 = [
                    np.complex(v[1],v[2]),
                    np.complex(v[3],v[4]),
                    np.complex(v[5],v[6]),
                ]
                try:
                    out[c].extend([H1, H2, H3])
                except KeyError:
                    out[c] = [H1, H2, H3]
            return out

        self = parse_block(t1, self)
        self = parse_block(t2, self)
        return self


    @classmethod
    def load(cls, url):
        if not hasattr(cls, 'ua'):
            cls.ua = requests_cache.CachedSession(
                'http_cache',
                expire_after=60*60*24*30)  #  month
        return cls.parse(cls.ua.get(url).text)


    @classmethod
    def load_kinematics(cls, **kvargs):
        url = furl(cls.url)
        if kvargs.get('Q2') is not None:
            url.args['value35'] = kvargs['Q2']
        if kvargs.get('W') is not None:
            W = kvargs['W'] * 1000  ##  GeV to MeV, MAID site uses MeV for W
            W = "{:g}".format(W)    ##  drop insignificant fluctuations
            url.args['value36'] = W
        if kvargs.get('FS') is not None:
            FS = kvargs['FS']
            FS_idx = {
                "pi0 p": 1,
                "pi0 n": 2,
                "pi+ n": 3,
                "pi- p": 4,
            }[FS]
            url.args['param2'] = FS_idx
        try:
            self = cls.load(url)
            if FS is not None:
                self.FS = FS
            return self
        except ValueError as e:
            print(
                'ERROR processing url for Q2={} and W={}\n{}\n'.format(
                    kvargs['Q2'], kvargs['W'], str(url)))
            raise

from sqlalchemy.orm import exc


def store_maid(ses, maid, nocommit=False):
    FS = maid.FS
    if not FS:
        FS = 'pi0 p'
    ch = Channel.query.filter_by(name=FS).one()
    try:
        m = Model.query.filter_by(name='maid').one()
    except exc.NoResultFound:
        m = Model(
            name="maid",
            author='MAID',
            description='MAID',
            )
    for k, v in maid.items():
        a = Amplitude(
            q2=maid.Q2,
            w=maid.W,
            cos_theta=k,
            channel=ch)

        # convert units since on site H units are in 10^-3/m_pi+
        v = np.array(v) / 1000 / hep.m_pi

        a.H = [None] + list(v)
        a.strfuns = hep.amplitudes.ampl_to_strfuns(a.H)
        m.amplitudes.append(a)
    # pprint(m)
    ses.add(m)
    if not nocommit:
        ses.commit()


class MAIDObservables(MAIDData):
    url = "https://maid.kph.uni-mainz.de/cgi-bin/maid1?switch=211&param2=1&param50=3&value35=0.5&value36=2000&value37=0&value41=10&value42=180&param99=0&param11=1&param12=1&param13=1&param14=1&param15=1&param16=1&param17=1&param18=1&param19=1&param20=1&param21=1&param22=1&param23=1&param24=1&param25=1&param26=1&value11=1.0&value12=1.0&value13=1.0&value51=1.0&value52=1.0&value53=1.0&value54=1.0&value55=1.0&value56=1.0&value57=1.0&value58=1.0&value59=1.0&value60=1.0&value61=1.0&value62=1.0&value63=1.0&value64=1.0&value65=1.0&value66=1.0&value67=1.0&value68=1.0&value69=1.0&value70=1.0&value71=1.0&value72=1.0&value73=1.0&value74=1.0&value75=1.0&value76=1.0&value77=1.0&value78=1.0&value79=1.0&value80=1.0&value81=1.0&value82=1.0&value83=1.0&value84=1.0"

    @classmethod
    def parse(cls, text):
        self = cls()
        self.get_kinematics(text)

        mo = re.search(r"""
                \s+\(deg\) .*? \n
                ([\s\d\.\-]*) \n
            """,
            text, re.M+re.S+re.X)

        t = mo.group(1)
        # print('GROUP:\n', t)

        for line in t.split("\n"):
            v = [float(x) for x in line.split()]
            c, dsT, dsL, dsTT, dsTL, dsTLp, dsT31, w_lab, w_cm, qpi_cm = v
            c = np.cos(np.deg2rad(c))
            if np.isclose(c, 0):
                c = 0
            self[c] = [dsT, dsL, dsTT, dsTL, dsTLp]

        return self


from clasfw.app import create_app
from clasfw.extensions import db
import click


def download_maid_amplitudes(q2, w, fs):
    app = create_app()
    with app.test_request_context():
        for FS in fs:
            for Q2 in q2:
                for W in w:
                    out = MAIDData.load_kinematics(Q2=Q2, W=W, FS=FS)
                    print("Q2={}, W={}, FS={}".format(out.Q2, out.W, out.FS))
                    # pprint(out)
                    store_maid(db.session, out, nocommit=True)
                db.session.commit()


@click.command()
@click.option("--Q2")
@click.option("--W")
@click.option("--FS", default="pi0 p")
def main_command(q2, w, fs):
    q2 = np.array(q2.split(','))
    w  = np.array( w.split(','))
    fs = [s.strip() for s in fs.split(',')]
    download_maid_amplitudes(q2, w, fs)


if __name__ == '__main__':
    # main_command()

    # download_maid_amplitudes([0.5, 1], [1.5, 2], ["pi0 p"])

    # W = np.arange(1.1, 2.00001, 0.1)

    download_maid_amplitudes(
        np.arange(0,   5.00001, 0.1),
        np.arange(1.1, 2.00001, 0.1),
        ["pi0 p", "pi0 n", "pi+ n", "pi- p"],
    )
