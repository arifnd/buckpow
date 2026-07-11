import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'powerdash-dev-key-change-in-production')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'buckpow.db')}"
    )

    HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    PORT: int = int(os.getenv('APP_PORT', 5001))
    DEBUG: bool = os.getenv('APP_ENV', 'development') == 'development'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'info')

    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', '')
    ADMIN_PASSWORD: str = os.getenv('ADMIN_PASSWORD', '')

    DEVICE_ONLINE_TIMEOUT: int = int(os.getenv('DEVICE_ONLINE_TIMEOUT', 30))
    DEFAULT_SAMPLING_INTERVAL: int = int(os.getenv('DEFAULT_SAMPLING_INTERVAL', 1))
    DISABLE_API_DOCS: bool = os.getenv('DISABLE_API_DOCS', '').lower() in ('true', '1', 'yes')

    if not SECRET_KEY and os.getenv('APP_ENV', 'development') == 'production':
        raise RuntimeError('SECRET_KEY environment variable is required in production')


settings = Settings()
