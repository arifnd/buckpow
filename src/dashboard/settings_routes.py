from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/settings")
def settings_page(current_user: CurrentUserDep):
    return _render_or_redirect("settings/index.html", current_user, "settings")
