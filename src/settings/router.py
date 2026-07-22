from datetime import datetime, timezone
import gzip
import os
import shutil
import subprocess
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from src.database import get_db, engine
from src.dependencies import require_user
from src.auth.models import User
from src.settings.schemas import SettingsUpdate

router = APIRouter()


def _detect_db_type() -> str:
    url = str(engine.url)
    if url.startswith("sqlite"):
        return "sqlite"
    if url.startswith("postgresql"):
        return "postgresql"
    if url.startswith("mysql"):
        return "mysql"
    return "unknown"


def _get_db_size() -> int | None:
    db_type = _detect_db_type()
    url = str(engine.url)
    if db_type == "sqlite":
        if url.startswith("sqlite:///"):
            db_path = url[10:]
        elif url.startswith("sqlite://"):
            db_path = url[9:]
        else:
            return None
        if not os.path.isabs(db_path):
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "instance",
                db_path,
            )
        if os.path.exists(db_path):
            return os.path.getsize(db_path)
    return None


def _parse_pg_url():
    parsed = urlparse(str(engine.url))
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username or "",
        "password": parsed.password or "",
    }


def _parse_mysql_url():
    parsed = urlparse(str(engine.url))
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username or "",
        "password": parsed.password or "",
    }


ALLOWED = {
    "high_power_threshold",
    "high_current_threshold",
    "low_voltage_threshold",
    "brand",
    "timestamp_format",
    "date_format",
    "timezone",
    "device_watchdog_timeout",
}


@router.get("/settings")
def get_settings(current_user: User = Depends(require_user)):
    return current_user.settings or {}


@router.put("/settings")
def update_settings(
    body: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    current = dict(current_user.settings or {})
    data = body.model_dump(exclude_none=True)
    for key, value in data.items():
        if key in ALLOWED:
            if value == "" or value is None:
                current.pop(key, None)
            else:
                current[key] = value
    current_user.settings = current
    db.commit()
    return current


@router.get("/settings/db-info")
def db_info(current_user: User = Depends(require_user)):
    db_type = _detect_db_type()
    size = _get_db_size()
    tools = {
        "sqlite": True,
        "postgresql": shutil.which("pg_dump") is not None,
        "mysql": shutil.which("mysqldump") is not None,
    }
    return {
        "type": db_type,
        "size": size,
        "backup_formats": {
            "sqlite": db_type == "sqlite",
            "sql_dump": db_type in ("postgresql", "mysql"),
        },
        "tool_available": tools.get(db_type, False),
    }


@router.get("/settings/backup")
def backup_database(current_user: User = Depends(require_user)):
    db_type = _detect_db_type()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")

    if db_type == "sqlite":
        return _backup_sqlite(ts)
    if db_type == "postgresql":
        return _backup_postgresql(ts)
    if db_type == "mysql":
        return _backup_mysql(ts)
    raise HTTPException(status_code=400, detail="Unsupported database engine")


def _backup_sqlite(ts: str):
    db_url = str(engine.url)
    if db_url.startswith("sqlite:///"):
        db_path = db_url[10:]
    elif db_url.startswith("sqlite://"):
        db_path = db_url[9:]
    else:
        raise HTTPException(status_code=400, detail="Invalid SQLite URL")

    if not os.path.isabs(db_path):
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "instance",
            db_path,
        )

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database file not found")

    with open(db_path, "rb") as f:
        content = f.read()
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=buckpow-backup-{ts}.db"},
    )


def _backup_postgresql(ts: str):
    pg_dump = shutil.which("pg_dump")
    if not pg_dump:
        raise HTTPException(status_code=500, detail="pg_dump not found on server")

    creds = _parse_pg_url()
    filename = f"buckpow-backup-{ts}.sql.gz"

    env = os.environ.copy()
    if creds["password"]:
        env["PGPASSWORD"] = creds["password"]

    cmd = [
        pg_dump,
        "-h",
        creds["host"],
        "-p",
        str(creds["port"]),
        "-U",
        creds["user"],
        "-d",
        creds["dbname"],
        "--no-owner",
        "--no-acl",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=120, env=env)
        if proc.returncode != 0:
            raise HTTPException(
                status_code=500, detail=f"pg_dump failed: {proc.stderr.decode()}"
            )
        compressed = gzip.compress(proc.stdout)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="pg_dump timed out")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="pg_dump not found")

    return Response(
        content=compressed,
        media_type="application/gzip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _backup_mysql(ts: str):
    mysqldump = shutil.which("mysqldump")
    if not mysqldump:
        raise HTTPException(status_code=500, detail="mysqldump not found on server")

    creds = _parse_mysql_url()
    filename = f"buckpow-backup-{ts}.sql.gz"

    cmd = [
        mysqldump,
        "-h",
        creds["host"],
        "-P",
        str(creds["port"]),
        "-u",
        creds["user"],
    ]
    if creds["password"]:
        cmd += ["-p" + creds["password"]]
    cmd.append(creds["dbname"])

    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=120)
        if proc.returncode != 0:
            raise HTTPException(
                status_code=500, detail=f"mysqldump failed: {proc.stderr.decode()}"
            )
        compressed = gzip.compress(proc.stdout)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="mysqldump timed out")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="mysqldump not found")

    return Response(
        content=compressed,
        media_type="application/gzip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
