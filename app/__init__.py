import logging
import sys

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.utils.rate_limiter import RateLimiterMiddleware, bearer_token_key

APP_VERSION = '0.1.0'


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if 'sqlite' in settings.DATABASE_URL:
        Base.metadata.create_all(bind=engine)
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config('alembic.ini')
            command.stamp(alembic_cfg, 'head')
        except Exception:
            logger.warning("Could not stamp alembic revision (non-fatal)")
    from app.models import User
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(User).first():
            if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
                from app.services.user_service import UserService
                UserService.create(
                    db=db,
                    name='Admin',
                    email=settings.ADMIN_EMAIL,
                    password=settings.ADMIN_PASSWORD,
                    commit=True,
                )
                logger.info("Admin user created (%s).", settings.ADMIN_EMAIL)
            else:
                logger.info("No users found and ADMIN_EMAIL/ADMIN_PASSWORD not set — skipping auto-create.")
        db.commit()
    finally:
        db.close()

    yield


app = FastAPI(title='BuckPow', version=APP_VERSION, lifespan=lifespan)

app.add_middleware(
    RateLimiterMiddleware,
    limits=[
        ('POST', '/api/v1/auth/login', 5, 60),
        ('POST', '/api/v1/measurements', 60, 60, bearer_token_key),
        ('GET', '/api/v1/measurements/export/csv', 10, 60),
        ('GET', '/api/v1/measurements/export/xlsx', 10, 60),
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='app/static'), name='static')

from app.api import api_router
from app.dashboard import dashboard_router

app.include_router(api_router, prefix='/api/v1')
app.include_router(dashboard_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from app.utils.errors import AppError
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={'error': exc.message, 'code': exc.code},
        )
    logging.getLogger(__name__).error('Internal server error', exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={'error': 'Internal server error', 'code': 'INTERNAL_ERROR'},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': exc.detail, 'code': 'ERROR'},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    if request.url.path.startswith('/api/'):
        return JSONResponse(
            status_code=404,
            content={'error': 'Not found', 'code': 'NOT_FOUND'},
        )
    return JSONResponse(status_code=404, content={'detail': 'Not Found'})


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: Exception):
    if request.url.path.startswith('/api/'):
        return JSONResponse(
            status_code=405,
            content={'error': 'Method not allowed', 'code': 'METHOD_NOT_ALLOWED'},
        )
    return JSONResponse(status_code=405, content={'detail': 'Method Not Allowed'})
