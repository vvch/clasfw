# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from webtest import TestApp

from clasfw.app import create_app
# from clasfw.database import db as _db
from clasfw.extensions import db as _db
from clasfw.settings import TestConfig

# from .factories import UserFactory


@pytest.fixture
def app():
    """Create application for the tests."""
    # _app = create_app("tests.settings")
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()
