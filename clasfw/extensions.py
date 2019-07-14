"""Extensions module. Each extension is initialized in the app factory located in app.py."""

from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_assets import Environment


db             = SQLAlchemy()
migrate        = Migrate()
assets         = Environment()
debug_toolbar  = DebugToolbarExtension()
