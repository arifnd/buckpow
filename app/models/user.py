from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, JSON

from app.database import Base
from app.utils.hash import hash_password, verify_password


class User(Base):
    __tablename__ = 'users'

    is_authenticated = True

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password = Column(String(256), nullable=False)
    settings = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    def set_password(self, password):
        self.password = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.email}>'
