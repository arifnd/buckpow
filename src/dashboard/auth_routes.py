from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from src.auth.models import User
from src.dependencies import CurrentUserDep, DbDep
from src.template_helpers import _render

router = APIRouter()


@router.get("/auth/login")
def login_page(current_user: CurrentUserDep, db: DbDep):
    if current_user:
        return RedirectResponse(url="/", status_code=302)
    brand = "BuckPow"
    user = db.query(User).first()
    if user and user.settings and user.settings.get("brand"):
        brand = user.settings["brand"]
    return HTMLResponse(
        _render("auth/login.html", current_user=current_user, brand_name=brand)
    )


@router.post("/auth/logout")
def logout_page():
    return {"status": "ok"}
