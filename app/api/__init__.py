from fastapi import APIRouter

from .health import router as health_router
from .measurements import router as measurements_router
from .dashboard import router as dashboard_router
from .devices import router as devices_router
from .sessions import router as sessions_router
from .auth import router as auth_router
from .projects import router as projects_router
from .alerts import router as alerts_router
from .benchmark import router as benchmark_router
from .settings import router as settings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(measurements_router)
api_router.include_router(dashboard_router)
api_router.include_router(devices_router)
api_router.include_router(sessions_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(alerts_router)
api_router.include_router(benchmark_router)
api_router.include_router(settings_router)
