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
