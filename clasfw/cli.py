import os
import click

from sqlalchemy import or_

from .models import Amplitude, Model
from .extensions import db
import hep.amplitudes
import flask_migrate

from .generate_content import create_dictionaries, generate_test_content, generate_all


def register(app):
    @app.cli.group()
    def gen():
        """Database content generation commands."""
        pass

    @gen.command()
    @click.option('-v', '--verbose', count=True)
    def all(verbose):
        """Generate all DB content."""
        generate_all(verbose)

    @gen.command()
    def dict():
        """Generate dictionary tables content."""
        create_dictionaries()

    @gen.command()
    @click.option('-v', '--verbose', count=True)
    def models(verbose):
        """Generate dummy models data."""
        generate_test_content()

    @gen.command()
    @click.option('-v', '--verbose', count=True)
    def create(verbose):
        """Create all database tables."""
        db.create_all()
        flask_migrate.stamp()


    @gen.command()
    @click.option('-v', '--verbose', count=True)
    @click.option('-m', '--models', multiple=True, type=str)
    @click.option('-i', '--ids', multiple=True, type=int)
    def rfuncs(verbose, models, ids):
        """Calculate response functions R^00_i."""

        cond = []
        m_list = []
        for mmm in models:
            for m in mmm.split(','):
                try:
                    c = Amplitude.model_id == int(m)
                    m_list.append(int(m))
                except ValueError:
                    c = Model.name == str(m)
                    m_list.append(str(m))
                cond.append(c)
        for i in ids:
            c = Amplitude.id == i
            cond.append(c)

        if verbose >=0:
            print("Calculating structure functions...")
            print("    for models ", m_list)

        counter = 0
        # print(cond)
        for a in Amplitude.query.join(Model).filter(or_(*cond)):
            if verbose >=1:
                print(a.H)
            a.strfuns = hep.amplitudes.ampl_to_strfuns(a.H)
            db.session.add(a)
            counter +=1
        if verbose >0:
            print("Calculated strfuns for {} amplitudes data points".format(counter))
            print("Committing to the database...")
            print("DEBUG: BEFORE COMMIT")
        db.session.commit()
        if verbose >0:
            print("DEBUG: AFTER COMMIT")
        if verbose >=0:
            print("DONE.")
