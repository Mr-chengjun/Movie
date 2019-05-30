from flask import Flask, render_template
from config import Config
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
import redis
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
# 创建redis连接对象
redis_store = None
mail = Mail()
dropzone = Dropzone()

migrate = Migrate()

login_manager.session_protection = "strong"
# login_manager.login_view = "admin.login"
login_manager.blueprint_login_views = {
    "home": "home.login",
    "admin": "admin.login"
}

login_manager.login_message_category = "warning"
login_manager.login_message = u"请先登录"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    bootstrap.init_app(app)
    # 初始化redis工具
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    dropzone.init_app(app)
    migrate.init_app(app, db)

    from app.home import home as home_blueprint
    from app.admin import admin as admin_blueprint
    app.register_blueprint(home_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    # 错误处理页面
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("home/404.html"), 404

    app.app_context().push()
    return app
