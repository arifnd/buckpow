from sqlalchemy.orm import Session
from src.auth.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id):
        return self.db.get(User, user_id)

    def get_by_email(self, email):
        return self.db.query(User).filter_by(email=email).first()

    def create(self, name, email, password, commit=True):
        existing = self.get_by_email(email)
        if existing:
            raise ValueError(f"User with email {email} already exists")
        user = User(name=name, email=email)
        user.set_password(password)
        self.db.add(user)
        if commit:
            self.db.commit()
        return user

    def update(self, user_id, name=None, email=None, password=None):
        user = self.db.get(User, user_id)
        if not user:
            return None
        if name is not None:
            user.name = name
        if email is not None:
            existing = self.get_by_email(email)
            if existing and existing.id != user_id:
                raise ValueError(f"Email {email} already in use")
            user.email = email
        if password:
            user.set_password(password)
        self.db.commit()
        return user

    def authenticate(self, email, password):
        user = self.get_by_email(email)
        if not user or not user.check_password(password):
            return None
        return user
