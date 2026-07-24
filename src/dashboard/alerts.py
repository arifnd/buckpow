from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/alerts")
def alerts_page(current_user: CurrentUserDep):
    return _render_or_redirect("alerts/index.html", current_user, "alerts")
