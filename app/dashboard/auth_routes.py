from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import User
from app.template_helpers import _render, _require_dashboard_user

router = APIRouter()


@router.get('/auth/login')
def login_page(current_user: User | None = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user:
        return RedirectResponse(url='/', status_code=302)
    brand = 'BuckPow'
    user = db.query(User).first()
    if user and user.settings and user.settings.get('brand'):
        brand = user.settings['brand']
    return HTMLResponse(_render('auth/login.html', current_user=current_user, brand_name=brand))


@router.post('/auth/logout')
def logout_page():
    return {'status': 'ok'}
