from fastapi import APIRouter

from src.dependencies import CurrentUserDep
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/projects")
def projects_page(current_user: CurrentUserDep):
    return _render_or_redirect("projects/index.html", current_user, "projects")
