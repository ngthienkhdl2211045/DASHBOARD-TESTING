import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'doi-key-nay-khi-deploy-that')

    # SQLite cho local/demo. Khi deploy thật lên Render, đổi sang PostgreSQL
    # bằng cách set biến môi trường DATABASE_URL (xem README.md)
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///dashboard.db')
    if db_url.startswith('postgres://'):
        # Render trả về postgres:// nhưng SQLAlchemy cần postgresql://
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.calendar import calendar_bp
    from app.routes.chat import chat_bp
    from app.routes.data import data_bp
    from app.routes.account import account_bp
    from app.routes.admin import admin_bp
    from app.routes.notifications import notif_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(data_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notif_bp)

    with app.app_context():
        db.create_all()

    return app
