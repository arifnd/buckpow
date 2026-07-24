from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/profile")
def profile_page(current_user: CurrentUserDep):
    return _render_or_redirect("auth/profile.html", current_user, "profile")
