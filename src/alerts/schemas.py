from enum import StrEnum

from pydantic import BaseModel, Field


class AlertLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCreate(BaseModel):
    device_id: int
    level: AlertLevel = AlertLevel.WARNING
    message: str
