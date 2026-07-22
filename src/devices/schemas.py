from pydantic import BaseModel


class DeviceCreate(BaseModel):
    device_id: str
    alias: str = ""
    description: str = ""
    sampling_interval: int | None = None
    project_id: int | None = None
    firmware_version: str = ""
    high_current_threshold: float | None = None
    high_power_threshold: float | None = None
    low_voltage_threshold: float | None = None


class DeviceUpdate(BaseModel):
    alias: str | None = None
    description: str | None = None
    sampling_interval: int | None = None
    project_id: int | None = None
    firmware_version: str | None = None
    enabled: bool | None = None
    high_current_threshold: float | None = None
    high_power_threshold: float | None = None
    low_voltage_threshold: float | None = None
