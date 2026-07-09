import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'powerdash-dev-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'bakpow.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
    DEBUG = False

    DEVICE_ONLINE_TIMEOUT = int(os.getenv('DEVICE_ONLINE_TIMEOUT', 30))
    DEFAULT_SAMPLING_INTERVAL = int(os.getenv('DEFAULT_SAMPLING_INTERVAL', 1))

    HIGH_CURRENT_THRESHOLD = float(os.getenv('HIGH_CURRENT_THRESHOLD', 0.5))
    HIGH_POWER_THRESHOLD = float(os.getenv('HIGH_POWER_THRESHOLD', 2.5))
    LOW_VOLTAGE_THRESHOLD = float(os.getenv('LOW_VOLTAGE_THRESHOLD', 4.5))


class DevConfig(Config):
    DEBUG = True
