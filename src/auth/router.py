from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.dependencies import create_access_token, get_current_user, require_user
from src.database import get_db
from src.auth.service import UserService
from src.audit.service import AuditService
from src.utils.client_ip import get_client_ip
from src.auth.models import User
from src.config import settings
from src.auth.schemas import LoginRequest, ProfileUpdate

router = APIRouter()


@router.post('/auth/login')
def login(body: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    email = body.email.strip()
    password = body.password
    if not email or not password:
        raise HTTPException(status_code=400, detail='Email and password are required')
    user = UserService(db).authenticate(email, password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid email or password')
    token = create_access_token(data={'sub': user.id})
    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        samesite='lax',
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    ip = get_client_ip(request)
    AuditService(db).log('login', user_id=user.id, ip_address=ip)
    return {'status': 'ok', 'user': user.to_dict(), 'token': token}


@router.post('/auth/logout')
def logout(response: Response):
    response.delete_cookie(key='access_token')
    return {'status': 'ok'}


@router.put('/auth/profile')
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_user)):
    try:
        user = UserService(db).update(current_user.id,
            name=body.name,
            email=body.email,
            password=body.password or None,
        )
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        return {'status': 'ok', 'user': user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get('/auth/me')
def me(current_user: User | None = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail='Not authenticated')
    return current_user.to_dict()
