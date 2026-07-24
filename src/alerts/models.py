from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base
from src.utils.dates import utc_iso


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    level = Column(String(16), nullable=False, default="warning")
    message = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    device_rel = relationship("Device", backref="alerts", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device_rel.device_id if self.device_rel else None,
            "level": self.level,
            "message": self.message,
            "created_at": utc_iso(self.created_at) if self.created_at else None,
            "resolved_at": utc_iso(self.resolved_at) if self.resolved_at else None,
        }

    def __repr__(self):
        return f"<Alert {self.level}: {self.message[:40]}>"
