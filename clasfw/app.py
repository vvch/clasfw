import os
from flask import Flask, render_template

from .settings import ProdConfig, DevConfig
from .extensions import db, migrate, assets, debug_toolbar
from .clasfw.blueprint import blueprint
from .clasfw import views, views_comparison, views_interpolate


def create_app(config_object=None):
    """An application factory"""

    if config_object is None:
        if os.environ.get('FLASK_ENV') == 'development':
            config_object = DevConfig
        # elif os.environ.get('FLASK_ENV') == 'production':
        else:
            config_object = ProdConfig

    app = Flask(__name__)
    # app.config.from_pyfile('settings.py')
    app.config.from_object(config_object)
    if os.environ.get('FLASK_ENV') in ('development', 'production'):
        app.config.from_pyfile('settings_local.py', silent=True)

    app.jinja_env.line_statement_prefix = '%'
    app.jinja_env.line_comment_prefix = '##'
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_blueprints(app):
    app.register_blueprint(blueprint)


def register_extensions(app):
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
        'base.styl',
        'views.styl',
        filters='stylus',
        output='gen/screen.css')

    assets.register('js_modellist',
        'model_list.js',
        output='gen/model_list.js')

    # if 0: #app.debug:
    #     from flask_debugtoolbar import DebugToolbarExtension
    #     debug_toolbar = DebugToolbarExtension()
    #     debug_toolbar.init_app(app)


def register_errorhandlers(app):

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template("{0}.html".format(error_code)), error_code

    for errcode in [404, 500]:
    # for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
