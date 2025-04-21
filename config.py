import os
from datetime import timedelta

from dotenv import load_dotenv

# 加载.env文件中的环境变量
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'say-more-teacher-secret-key')
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)
    SESSION_COOKIE_NAME = "teacher_session"
    SESSION_COOKIE_PATH = "/"  # 修改为根路径
    SESSION_COOKIE_SECURE = False  # 非https环境
    SESSION_COOKIE_HTTPONLY = True  # 防止JS访问cookie
    SESSION_COOKIE_SAMESITE = "Lax"  # 限制第三方站点访问

    WTF_CSRF_ENABLED = False

    # 数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'saynore')

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', False)


    # 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
    }

    # 阿里云OSS配置
    OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID', '')
    OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET', '')
    OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME', '')
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT', '')
    OSS_BUCKET_URL = os.environ.get('OSS_BUCKET_URL', '')
    UPLOAD_USE_OSS = os.environ.get('UPLOAD_USE_OSS', False)

    # 阿里云短信服务配置
    SMS_ACCESS_KEY_ID = os.environ.get('SMS_ACCESS_KEY_ID', '')
    SMS_ACCESS_KEY_SECRET = os.environ.get('SMS_ACCESS_KEY_SECRET', '')
    SMS_SIGN_NAME = os.environ.get('SMS_SIGN_NAME', 'saynore')
    SMS_TEMPLATE_CODE = os.environ.get('SMS_TEMPLATE_CODE', '')

    # 分页配置
    ITEMS_PER_PAGE = os.environ.get('ITEMS_PER_PAGE', 10)

    # 验证码配置
    SMS_CODE_EXPIRY_SECONDS = 300  # 5分钟
    SMS_CODE_RESEND_LIMIT_SECONDS = 60  # 60秒内不能重复发送
