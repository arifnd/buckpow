import os

from app import create_app
from app.config import Config, DevConfig

config = DevConfig if os.getenv('FLASK_ENV', 'development') == 'development' else Config
app = create_app(config)

if __name__ == '__main__':
    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
