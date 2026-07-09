from flask import Blueprint
from .health import health_bp
from .measurements import measurements_bp
from .dashboard import dashboard_bp
from .devices import devices_bp
from .sessions import sessions_bp
from .auth import auth_bp
from .projects import projects_bp
from .alerts import alerts_bp
from .benchmark import benchmark_bp

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(health_bp)
api_bp.register_blueprint(measurements_bp)
api_bp.register_blueprint(dashboard_bp)
api_bp.register_blueprint(devices_bp)
api_bp.register_blueprint(sessions_bp)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(projects_bp)
api_bp.register_blueprint(alerts_bp)
api_bp.register_blueprint(benchmark_bp)
