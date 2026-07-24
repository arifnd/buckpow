from src.models import AppBaseModel


class MeasurementCreate(AppBaseModel):
    device_id: str
    bus_voltage: float
    shunt_voltage: float = 0.0
    current: float
    power: float
    firmware_version: str | None = None
