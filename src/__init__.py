import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src import database as db_module
from src.config import settings as config
from src.dashboard import dashboard_router
from src.database import Base
from src.middleware import RateLimiterMiddleware, bearer_token_key
from src.router import api_router
from src.version import APP_VERSION as APP_VERSION
from src.version import MIN_FIRMWARE_VERSION as MIN_FIRMWARE_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if "sqlite" in config.DATABASE_URL:
        db_path = db_module.engine.url.database
        if db_path:
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        Base.metadata.create_all(bind=db_module.engine)
        try:
            from alembic import command
            from alembic.config import Config

            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, "head")
        except Exception:
            logger.warning("Could not stamp alembic revision (non-fatal)")
    from src.auth.models import User
    from src.database import SessionLocal

    db = SessionLocal()
    try:
        if not db.query(User).first():
            if config.ADMIN_EMAIL and config.ADMIN_PASSWORD:
                from src.auth.service import UserService

                UserService(db).create(
                    name="Admin",
                    email=config.ADMIN_EMAIL,
                    password=config.ADMIN_PASSWORD,
                    commit=True,
                )
                logger.info("Admin user created (%s).", config.ADMIN_EMAIL)
            else:
                logger.info(
                    "No users found and ADMIN_EMAIL/ADMIN_PASSWORD not set — skipping auto-create."
                )
        db.commit()
    finally:
        db.close()

    yield


SHOW_DOCS_IN = {"development", "staging"}
disable_docs = config.DISABLE_API_DOCS or config.APP_ENV not in SHOW_DOCS_IN

app = FastAPI(
    title="BuckPow",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url=None if disable_docs else "/docs",
    redoc_url=None if disable_docs else "/redoc",
    openapi_url=None if disable_docs else "/openapi.json",
)

app.add_middleware(
    RateLimiterMiddleware,
    limits=[
        ("POST", "/api/v1/auth/login", 5, 60),
        ("POST", "/api/v1/measurements", 60, 60, bearer_token_key),
        ("GET", "/api/v1/measurements/export/csv", 10, 60),
        ("GET", "/api/v1/measurements/export/xlsx", 10, 60),
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(api_router, prefix="/api/v1")
app.include_router(dashboard_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from src.utils.errors import AppError

    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "code": exc.code},
        )
    logging.getLogger(__name__).error("Internal server error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": "ERROR"},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found", "code": "NOT_FOUND"},
        )
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=405,
            content={"error": "Method not allowed", "code": "METHOD_NOT_ALLOWED"},
        )
    return JSONResponse(status_code=405, content={"detail": "Method Not Allowed"})
