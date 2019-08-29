"""Extensions module. Each extension is initialized in the app factory located in app.py."""

from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_assets import Environment

from sqlalchemy import MetaData


# According to
# https://stackoverflow.com/questions/45527323/flask-sqlalchemy-upgrade-failing-after-updating-models-need-an-explanation-on-h

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db             = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate        = Migrate()
assets         = Environment()
debug_toolbar  = DebugToolbarExtension()
