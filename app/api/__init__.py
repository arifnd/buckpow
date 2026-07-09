from flask import Blueprint
from .measurements import measurements_bp
from .dashboard import dashboard_bp
from .devices import devices_bp
from .sessions import sessions_bp
from .auth import auth_bp

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(measurements_bp)
api_bp.register_blueprint(dashboard_bp)
api_bp.register_blueprint(devices_bp)
api_bp.register_blueprint(sessions_bp)
api_bp.register_blueprint(auth_bp)
