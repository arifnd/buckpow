from fastapi import APIRouter

router = APIRouter()

MIN_FIRMWARE_VERSION = '1.0.0'


@router.get('/health')
def health():
    return {'status': 'ok', 'min_firmware_version': MIN_FIRMWARE_VERSION}
