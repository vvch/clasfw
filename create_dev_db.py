import os

# shoul be set in environment!
# may not behave as expected if set in code
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_APP', 'clasfw:app.py')

os.environ.setdefault('WERKZEUG_DEBUG_PIN', 'off') # no PIN for browser debugger

from clasfw.app import create_app
from clasfw.settings import DevConfig
from clasfw.models import Base
from clasfw.extensions import db

app = create_app(DevConfig)
# db.create_all()

with app.test_request_context():
    # Base.metadata.create_all()
    db.create_all()
