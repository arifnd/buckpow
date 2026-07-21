from fastapi import APIRouter

from src.config import settings


MIN_FIRMWARE_VERSION = '1.0.0'

router = APIRouter()


@router.get('/health')
def health_check():
    return {
        'status': 'ok',
        'version': '0.1.0-beta.1',
        'min_firmware_version': MIN_FIRMWARE_VERSION,
    }
