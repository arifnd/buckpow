from app import db
from app.models import User


class UserService:

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(name, email, password):
        existing = UserService.get_by_email(email)
        if existing:
            raise ValueError(f'User with email {email} already exists')
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user_id, name=None, email=None, password=None):
        user = db.session.get(User, user_id)
        if not user:
            return None
        if name is not None:
            user.name = name
        if email is not None:
            existing = UserService.get_by_email(email)
            if existing and existing.id != user_id:
                raise ValueError(f'Email {email} already in use')
            user.email = email
        if password:
            user.set_password(password)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(email, password):
        user = UserService.get_by_email(email)
        if not user or not user.check_password(password):
            return None
        return user
