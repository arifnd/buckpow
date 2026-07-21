from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user
from app.models import User
from app.template_helpers import _render_or_redirect

router = APIRouter()


@router.get('/settings')
def settings_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect('settings/index.html', current_user, 'settings')
