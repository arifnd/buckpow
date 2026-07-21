from fastapi import APIRouter

from src import APP_VERSION, MIN_FIRMWARE_VERSION
from src.measurements.router import router as measurements_router
from src.dashboard.api import router as dashboard_api_router
from src.devices.router import router as devices_router
from src.sessions.router import router as sessions_router
from src.auth.router import router as auth_router
from src.projects.router import router as projects_router
from src.alerts.router import router as alerts_router
from src.benchmark.router import router as benchmark_router
from src.settings.router import router as settings_router
from src.audit.router import router as audit_router


health_router = APIRouter()


@health_router.get('/health')
def health_check():
    return {
        'status': 'ok',
        'version': APP_VERSION,
        'min_firmware_version': MIN_FIRMWARE_VERSION,
    }


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(measurements_router)
api_router.include_router(dashboard_api_router)
api_router.include_router(devices_router)
api_router.include_router(sessions_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(alerts_router)
api_router.include_router(benchmark_router)
api_router.include_router(settings_router)
api_router.include_router(audit_router)
