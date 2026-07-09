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
    def authenticate(email, password):
        user = UserService.get_by_email(email)
        if not user or not user.check_password(password):
            return None
        return user
