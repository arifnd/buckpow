from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
