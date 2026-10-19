from flask import Flask
from .config import Config
from .extensions import db, migrate
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models
    from .api import api_bp

    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app