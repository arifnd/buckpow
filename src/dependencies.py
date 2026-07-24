from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.auth.dependencies import (
    create_access_token,
    get_api_key_device,
    get_current_user,
    require_user,
)
from src.auth.models import User
from src.database import get_db

DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User | None, Depends(get_current_user)]
RequiredUserDep = Annotated[User, Depends(require_user)]

__all__ = [
    "create_access_token",
    "get_current_user",
    "require_user",
    "get_api_key_device",
    "get_db",
    "DbDep",
    "CurrentUserDep",
    "RequiredUserDep",
]
