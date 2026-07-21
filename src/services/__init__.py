from src.devices.service import DeviceService
from src.sessions.service import SessionService
from src.measurements.service import MeasurementService
from src.alerts.service import AlertService
from src.projects.service import ProjectService
from src.auth.service import UserService
from src.audit.service import AuditService
from src.dashboard.service import DashboardService


def device_service(db):
    return DeviceService(db)


def session_service(db):
    return SessionService(db)


def measurement_service(db):
    return MeasurementService(db)


def alert_service(db):
    return AlertService(db)


def project_service(db):
    return ProjectService(db)


def user_service(db):
    return UserService(db)


def audit_service(db):
    return AuditService(db)


def dashboard_service(db):
    return DashboardService(db)


__all__ = [
    'DeviceService', 'SessionService', 'MeasurementService',
    'AlertService', 'ProjectService', 'UserService', 'AuditService',
    'DashboardService',
    'device_service', 'session_service', 'measurement_service',
    'alert_service', 'project_service', 'user_service', 'audit_service',
    'dashboard_service',
]
