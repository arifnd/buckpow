from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.dependencies import get_current_user
from src.auth.models import User
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get('/alerts')
def alerts_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect('alerts/index.html', current_user, 'alerts')
