from enum import StrEnum

from src.models import AppBaseModel


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCreate(AppBaseModel):
    device_id: int
    level: AlertLevel = AlertLevel.WARNING
    message: str
