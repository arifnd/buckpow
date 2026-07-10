from sqlalchemy.orm import Session
from app.models import User


class UserService:

    @staticmethod
    def get_by_id(db: Session, user_id):
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email):
        return db.query(User).filter_by(email=email).first()

    @staticmethod
    def create(db: Session, name, email, password, commit=True):
        existing = UserService.get_by_email(db, email)
        if existing:
            raise ValueError(f'User with email {email} already exists')
        user = User(name=name, email=email)
        user.set_password(password)
        db.add(user)
        if commit:
            db.commit()
        return user

    @staticmethod
    def update(db: Session, user_id, name=None, email=None, password=None):
        user = db.get(User, user_id)
        if not user:
            return None
        if name is not None:
            user.name = name
        if email is not None:
            existing = UserService.get_by_email(db, email)
            if existing and existing.id != user_id:
                raise ValueError(f'Email {email} already in use')
            user.email = email
        if password:
            user.set_password(password)
        db.commit()
        return user

    @staticmethod
    def authenticate(db: Session, email, password):
        user = UserService.get_by_email(db, email)
        if not user or not user.check_password(password):
            return None
        return user
