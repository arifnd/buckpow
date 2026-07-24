from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    JWT_SECRET: str = Field(
        default="buckpow-dev-key-change-in-production", alias="SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""


auth_settings = AuthConfig()
