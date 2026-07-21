import os
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    JWT_SECRET: str = Field(default='buckpow-dev-key-change-in-production', alias='SECRET_KEY')
    JWT_ALGORITHM: str = Field(default='HS256', alias='ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = Field(
        default=f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'buckpow.db')}"
    )

    HOST: str = Field(default='0.0.0.0', alias='APP_HOST')
    PORT: int = Field(default=8000, alias='APP_PORT')
    LOG_LEVEL: str = Field(default='info')

    ADMIN_EMAIL: str = Field(default='')
    ADMIN_PASSWORD: str = Field(default='')

    DEVICE_ONLINE_TIMEOUT: int = Field(default=30)
    DEFAULT_SAMPLING_INTERVAL: int = Field(default=1)
    DEVICE_AUTH_ENABLED: bool = Field(default=True)
    DISABLE_API_DOCS: bool = Field(default=False)

    DEBUG: bool = Field(default=True, exclude=True)

    model_config = {'env_file': '.env', 'extra': 'ignore', 'populate_by_name': True}

    @model_validator(mode='after')
    def _derive_debug(self):
        env = os.getenv('APP_ENV', 'development')
        object.__setattr__(self, 'DEBUG', env == 'development')

        if not self.JWT_SECRET and env == 'production':
            raise RuntimeError('JWT_SECRET environment variable is required in production')
        if len(self.JWT_SECRET) < 32:
            import warnings
            warnings.warn(
                f'JWT_SECRET is {len(self.JWT_SECRET)} bytes (minimum 32 recommended for HMAC-SHA256)',
                UserWarning,
                stacklevel=2,
            )
        return self


settings = Settings()
