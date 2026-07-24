from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/measurements")
def measurements_page(current_user: CurrentUserDep):
    return _render_or_redirect("measurements/index.html", current_user, "measurements")
