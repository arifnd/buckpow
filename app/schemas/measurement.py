from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    device_id: str
    bus_voltage: float
    shunt_voltage: float
    current: float
    power: float
    firmware_version: str | None = None
