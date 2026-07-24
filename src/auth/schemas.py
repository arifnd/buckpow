from src.models import AppBaseModel


class LoginRequest(AppBaseModel):
    email: str
    password: str


class ProfileUpdate(AppBaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
