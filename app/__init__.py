import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from .config import config_map

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(config_name, config_map['development']))

    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp
    from .tasks import tasks_bp
    from .timetable import timetable_bp
    from .analytics import analytics_bp
    from .main_routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(analytics_bp)

    with app.app_context():
        db.create_all()

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200

    return app
