from pydantic_settings import BaseSettings, SettingsConfigDict


class DeviceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ONLINE_TIMEOUT: int = 30
    DEFAULT_SAMPLING_INTERVAL: int = 1
    AUTH_ENABLED: bool = True


device_settings = DeviceConfig()
