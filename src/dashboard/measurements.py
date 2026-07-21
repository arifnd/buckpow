from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.dependencies import get_current_user
from src.models import User
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get('/measurements')
def measurements_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect('measurements/index.html', current_user, 'measurements')
