from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import DevConfig

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=DevConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    CORS(flask_app)

    from .api import api_bp
    from .dashboard import dashboard_bp
    flask_app.register_blueprint(api_bp, url_prefix='/api/v1')
    flask_app.register_blueprint(dashboard_bp)

    import app.models

    @flask_app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database tables created.")

    return flask_app
