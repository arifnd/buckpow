from src.models import AppBaseModel


class ProjectCreate(AppBaseModel):
    name: str
    description: str = ""


class ProjectUpdate(AppBaseModel):
    name: str | None = None
    description: str | None = None
