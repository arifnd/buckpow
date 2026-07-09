import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY environment variable is required in production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'buckpow.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
    DEBUG = False

    DEVICE_ONLINE_TIMEOUT = int(os.getenv('DEVICE_ONLINE_TIMEOUT', 30))
    DEFAULT_SAMPLING_INTERVAL = int(os.getenv('DEFAULT_SAMPLING_INTERVAL', 1))

class DevConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY', 'powerdash-dev-key-change-in-production')
    DEBUG = True
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
