from .device_service import DeviceService
from .session_service import SessionService
from .measurement_service import MeasurementService
from .alert_service import AlertService
from .project_service import ProjectService
from .user_service import UserService
from .audit_service import AuditService
from .dashboard_service import DashboardService


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