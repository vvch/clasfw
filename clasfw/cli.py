import os
import click

from .models import Amplitude
from .extensions import db
import hep.amplitudes
import flask_migrate


def register(app):
    @app.cli.group()
    def gen():
        """Database content generation commands."""
        pass

    @gen.command()
    def all():
        """Generate all DB content."""
        pass

    @gen.command()
    def dict():
        """Generate dictionary tables content."""
        pass

    @gen.command()
    def models():
        """Generate dummy models data."""
        pass

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
