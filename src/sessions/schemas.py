from pydantic import BaseModel


class SessionCreate(BaseModel):
    device_id: int
    name: str
    target_device: str = ''
    description: str = ''
    project_id: int | None = None


class SessionUpdate(BaseModel):
    name: str | None = None
    target_device: str | None = None
    description: str | None = None
    project_id: int | None = None
