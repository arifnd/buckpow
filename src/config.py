import os
import warnings

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore", "populate_by_name": True}

    JWT_SECRET: str = Field(..., alias="SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = Field(default=f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'buckpow.db')}")

    HOST: str = Field(default="0.0.0.0", alias="APP_HOST")
    PORT: int = Field(default=8000, alias="APP_PORT")
    LOG_LEVEL: str = "info"

    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""

    DEVICE_ONLINE_TIMEOUT: int = 30
    DEFAULT_SAMPLING_INTERVAL: int = 1
    DEVICE_AUTH_ENABLED: bool = True
    DISABLE_API_DOCS: bool = False
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:8000", "http://127.0.0.1:8000"],
        alias="ALLOWED_ORIGINS",
    )
    MAX_AUTO_REGISTERED_DEVICES: int = Field(default=50, alias="MAX_AUTO_REGISTERED_DEVICES")

    DEBUG: bool = Field(default=True, exclude=True)

    def model_post_init(self, __context):
        env = self.APP_ENV
        object.__setattr__(self, "DEBUG", env == "development")

        if len(self.JWT_SECRET) < 32:
            warnings.warn(
                f"JWT_SECRET is {len(self.JWT_SECRET)} bytes (minimum 32 recommended for HMAC-SHA256)",
                UserWarning,
                stacklevel=2,
            )


settings = Settings()
