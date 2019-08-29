# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from clasfw.models import Model
from clasfw.extensions import db


@pytest.mark.usefixtures("db")
class TestModel:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        m = Model(
            name="test_model",
            author="somebody")
        # m.save()
        db.session.add(m)
        db.session.commit()

        retrieved = Model.query.get(m.id)
        assert retrieved == m
