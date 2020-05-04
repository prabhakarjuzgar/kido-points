import os
import logging
from pathlib import Path
from logging.config import fileConfig
from flask import Flask, request, current_app
from flask_babel import Babel, lazy_gettext as _l
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap


login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please login to access this page.')

db = SQLAlchemy()
babel = Babel()
bootstrap = Bootstrap()

# LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.cfg')
LOG_FILE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = LOG_FILE_PATH.parent
LOG_FILE = os.path.join(LOG_FILE_PATH, 'logging.cfg')
fileConfig(LOG_FILE, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ.get('APP_SETTINGS'))

    babel.init_app(app)
    db.init_app(app)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.main import bp as bp_main
    app.register_blueprint(bp_main)

    from app.auth import bp as bp_auth
    app.register_blueprint(bp_auth, url_prefix='/auth')

    from app.errors import bp as bp_error
    app.register_blueprint(bp_error)

    from app.models import User, Child, Target

    with app.app_context():
        db.create_all()
        return app
