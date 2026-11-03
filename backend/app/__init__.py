from flask import Flask

from . import config, db
from .routes import api, frontend_blueprint


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config["SECRET_KEY"] = config.secret_key()
    db.init_app(app, config.database_url())

    app.register_blueprint(api)
    frontend_dist = config.frontend_dist()
    if frontend_dist:
        app.register_blueprint(frontend_blueprint(frontend_dist))

    return app
