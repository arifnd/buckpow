from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db
from src.auth.models import User

security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def _decode_user(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.get(User, int(user_id))
    except (InvalidTokenError, ValueError, TypeError):
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    request: Request = None,
    db: Session = Depends(get_db),
) -> User | None:
    token = None
    if credentials is not None:
        token = credentials.credentials
    if token is None and request is not None:
        token = request.cookies.get("access_token")
    if token is None:
        return None
    return _decode_user(token, db)


def require_user(current_user: User | None = Depends(get_current_user)) -> User:
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return current_user


def get_api_key_device(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
):
    from src.devices.service import DeviceService

    if not settings.DEVICE_AUTH_ENABLED:
        return None
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    api_key = credentials.credentials
    device = DeviceService(db).get_by_api_key(api_key)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    if not device.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Device is disabled"
        )
    return device
