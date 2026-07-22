from fastapi import APIRouter, Depends

from src.dependencies import get_current_user
from src.auth.models import User
from src.template_helpers import _render_or_redirect

router = APIRouter()


@router.get("/benchmark")
def benchmark_page(current_user: User | None = Depends(get_current_user)):
    return _render_or_redirect("benchmark/index.html", current_user, "benchmark")
