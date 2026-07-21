from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    device_id: str
    bus_voltage: float
    shunt_voltage: float = 0.0
    current: float
    power: float
    firmware_version: str | None = None
