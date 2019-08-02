import os
import click

from .models import Amplitude
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
    def create():
        """Create all database tables."""
        db.create_all()
        flask_migrate.stamp()


    @gen.command()
    @click.option('-v', '--verbose', count=True)
    def strfuns(verbose):
        """Calculate structure functions."""
        # TODO: parameter 'models'
        if verbose >=0:
            print("Calculating structure functions...")
        for a in Amplitude.query.filter(
                # fixme: temporary!!!
                Amplitude.model_id.in_((1,2)),
                # Amplitude.id.in_((1,2,3,4))
            ).all():
            if verbose>0:
                print(a.a)
            a.strfuns = hep.amplitudes.ampl_to_strfuns(a.a)
            db.session.add(a)
        if verbose >0:
            print("Committing to the database...")
            print("DEBUG: BEFORE COMMIT")
        db.session.commit()
        if verbose >0:
            print("DEBUG: AFTER COMMIT")
        if verbose >=0:
            print("DONE.")
