import os


class Config(object):
    SECRET_KEY = 'secretkey'
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:123456@127.0.0.1:3306/movie"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 邮箱配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "smtp.qq.com"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 1 is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "1174948552@qq.com"
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "jpqvwnzeoequfeed"
    ADMINS = ['1174948552@qq.com']

    # 配置文件上传路径
    UPLOAD_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app/static/uploads/")
