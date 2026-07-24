from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DashboardConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    HOST: str = Field(default="0.0.0.0", alias="APP_HOST")
    PORT: int = Field(default=8000, alias="APP_PORT")
    LOG_LEVEL: str = "info"
    DISABLE_API_DOCS: bool = False
    APP_ENV: str = "development"
    DEBUG: bool = Field(default=True, exclude=True)


dashboard_settings = DashboardConfig()
