import os
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    SECRET_KEY: str = Field(default='powerdash-dev-key-change-in-production')
    ALGORITHM: str = 'HS256'
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
    DISABLE_API_DOCS: bool = Field(default=False)

    DEBUG: bool = Field(default=True, exclude=True)

    model_config = {'env_file': '.env', 'extra': 'ignore'}

    @model_validator(mode='after')
    def _derive_debug(self):
        env = os.getenv('APP_ENV', 'development')
        object.__setattr__(self, 'DEBUG', env == 'development')
        if not self.SECRET_KEY and env == 'production':
            raise RuntimeError('SECRET_KEY environment variable is required in production')
        return self


settings = Settings()
