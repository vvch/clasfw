from flask import Flask, request, render_template_string

from clasfw.settings import ProdConfig, DevConfig
from clasfw.extensions import db, migrate, assets, debug_toolbar
import clasfw.clasfw.blueprint
from clasfw.clasfw.blueprint import blueprint

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

    register_extensions(app)
    register_blueprints(app)
    # register_errorhandlers(app)
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(clasfw.clasfw.blueprint.blueprint)
    return None


def register_extensions(app):
    """Register Flask extensions."""

    db.init_app(app)
    migrate.init_app(app, db)
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

    # if 0: #app.debug:
    #     from flask_debugtoolbar import DebugToolbarExtension
    #     debug_toolbar = DebugToolbarExtension()
    #     debug_toolbar.init_app(app)

    return None


# @app.errorhandler(404)
# def error_page_not_found(e):
#     return render_template_string(
#         """
#         <html>
#         <head>
#         </head>
#         <body>
#             <h1>Page not found</h1>
#             <div>{{ path }}</div>
#         </body>
#         </html>
#         """, path=request.path), 404

# from clasfw.settings import DevConfig
import clasfw.clasfw.views
# app = create_app(DevConfig)  ##  temporary workaround
