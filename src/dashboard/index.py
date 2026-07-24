from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/")
def index(current_user: CurrentUserDep):
    return _render_or_redirect("dashboard/index.html", current_user, "dashboard")
