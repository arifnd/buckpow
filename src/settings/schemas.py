from pydantic import BaseModel


class SettingsUpdate(BaseModel):
    high_power_threshold: float | str | None = None
    high_current_threshold: float | str | None = None
    low_voltage_threshold: float | str | None = None
    brand: str | None = None
    timestamp_format: str | None = None
    date_format: str | None = None
    timezone: str | None = None
    device_watchdog_timeout: int | str | None = None
