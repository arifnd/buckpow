import logging
import sys

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager
from .config import DevConfig

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'dashboard.login'
login_manager.login_message_category = 'info'


APP_VERSION = '0.1.0'


def create_app(config_class=DevConfig):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    CORS(flask_app)
    login_manager.init_app(flask_app)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout,
    )
    flask_app.logger.setLevel(logging.INFO)

    from .api import api_bp
    from .dashboard import dashboard_bp
    from .utils.errors import AppError

    @flask_app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({'error': e.message, 'code': e.code}), e.status_code

    @flask_app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Bad request', 'code': 'BAD_REQUEST'}), 400
        return e

    @flask_app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found', 'code': 'NOT_FOUND'}), 404
        return e

    @flask_app.errorhandler(405)
    def method_not_allowed(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Method not allowed', 'code': 'METHOD_NOT_ALLOWED'}), 405
        return e

    @flask_app.errorhandler(500)
    def internal_error(e):
        flask_app.logger.error('Internal server error', exc_info=e)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500
        return e

    flask_app.register_blueprint(api_bp, url_prefix='/api/v1')
    flask_app.register_blueprint(dashboard_bp)

    import app.models

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    with flask_app.app_context():
        if 'sqlite' in flask_app.config['SQLALCHEMY_DATABASE_URI']:
            db.create_all()
            from app.models import User
            if not User.query.first():
                from app.services.user_service import UserService
                UserService.create(
                    name='Admin',
                    email='admin@example.com',
                    password='password',
                )

    @flask_app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        from app.models import User
        from app.services.user_service import UserService
        if not User.query.first():
            UserService.create(
                name='Admin',
                email='admin@bakpow.local',
                password='admin',
            )
            print("Default admin user created (admin@bakpow.local / admin).")
        print("Database tables created.")

    @flask_app.context_processor
    def inject_globals():
        return dict(app_version=APP_VERSION)

    return flask_app
