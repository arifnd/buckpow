import os

from app import create_app, db
from app.config import Config, DevConfig

config = DevConfig if os.getenv('FLASK_ENV', 'development') == 'development' else Config
app = create_app(config)

if __name__ == '__main__':
    with app.app_context():
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            db.create_all()
        from app.models import User
        if not User.query.first():
            from app.services.user_service import UserService
            UserService.create(
                name='Admin',
                email='admin@example.com',
                password='password',
            )
    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
