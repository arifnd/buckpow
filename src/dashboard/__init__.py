from fastapi import APIRouter

from .index import router as index_router
from .devices import router as devices_router
from .sessions import router as sessions_router
from .measurements import router as measurements_router
from .projects import router as projects_router
from .alerts import router as alerts_router
from .benchmark import router as benchmark_router
from .auth_routes import router as auth_router
from .profile import router as profile_router
from .settings_routes import router as settings_router
from .audit import router as audit_router

dashboard_router = APIRouter()
dashboard_router.include_router(index_router)
dashboard_router.include_router(devices_router)
dashboard_router.include_router(sessions_router)
dashboard_router.include_router(measurements_router)
dashboard_router.include_router(projects_router)
dashboard_router.include_router(alerts_router)
dashboard_router.include_router(benchmark_router)
dashboard_router.include_router(auth_router)
dashboard_router.include_router(profile_router)
dashboard_router.include_router(settings_router)
dashboard_router.include_router(audit_router)

__all__ = ["dashboard_router"]
