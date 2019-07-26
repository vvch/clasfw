from flask import Flask, request, render_template, render_template_string

from .settings import ProdConfig, DevConfig
from .extensions import db, migrate, assets, debug_toolbar
from .clasfw.blueprint import blueprint
from .clasfw import views

import os

def create_app(config_object=None):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    if config_object is None:
        if os.environ.get('FLASK_ENV') == 'development':
            config_object = DevConfig
        elif os.environ.get('FLASK_ENV') == 'production':
            config_object = ProdConfig

    app = Flask(__name__)
    # app.config.from_pyfile('settings.py')
    app.config.from_object(config_object)
    app.config.from_pyfile('settings_local.py', silent=True)
    # app.config.from_pyfile('settings_local.py')

    app.jinja_env.line_statement_prefix = '%'
    app.jinja_env.line_comment_prefix = '##'
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(blueprint)
    return None


def register_extensions(app):
    """Register Flask extensions."""

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    debug_toolbar.init_app(app)

    assets.init_app(app)

    # assets.debug = True
    # assets.append_path('assets')
    # assets.config['STYLUS_EXTRA_ARGS'] = [
    #     # Emits debug infos for the FireStylus Firebug plugin
    #     # '--firebug',
    #     # Emits comments in the generated CSS indicating
    #     # the corresponding Stylus line
    #     # '--line-numbers',
    # ]
    assets.register('css_screen',
        'base.styl', 'views.styl',
        filters='stylus',
        output='gen/screen.css')

    assets.register('js_modellist',
        'model_list.js',
        output='gen/model_list.js')

    # if 0: #app.debug:
    #     from flask_debugtoolbar import DebugToolbarExtension
    #     debug_toolbar = DebugToolbarExtension()
    #     debug_toolbar.init_app(app)

    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [404, 500]:
    # for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None
