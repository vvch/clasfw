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
    def all():
        """Generate all DB content."""
        generate_all()

    @gen.command()
    def dict():
        """Generate dictionary tables content."""
        create_dictionaries()

    @gen.command()
    def models():
        """Generate dummy models data."""
        generate_test_content()

    @gen.command()
    def create():
        """Create all database tables."""
        db.create_all()
        flask_migrate.stamp()


    @gen.command()
    def strfuns():
        """Calculate structure functions."""
        for a in Amplitude.query.filter(
                # fixme: temporary!!!
                Amplitude.model_id.in_((1,2))
            ).all():
            print(a.a)
            a.strfuns = hep.amplitudes.ampl_to_strfuns(a.a)
            db.session.add(a)
        db.session.commit()
