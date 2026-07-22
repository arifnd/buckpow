from pydantic import BaseModel


class AlertCreate(BaseModel):
    device_id: int
    level: str = "warning"
    message: str
