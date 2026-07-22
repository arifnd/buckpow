from fastapi import APIRouter, Depends

from src.dependencies import get_current_user
from src.auth.models import User
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/projects")
def projects_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect("projects/index.html", current_user, "projects")
