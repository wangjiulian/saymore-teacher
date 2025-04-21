from flask import Blueprint
from .auth import bp as auth_bp
from .profile import bp as profile_bp
from .course import bp as course_bp
from .availability import bp as availability_bp
from .base import bp as upload_bp
from .teacher import bp as teacher_bp
from .course_fee import bp as course_fee_bp

def init_app(app):
    """注册所有蓝图"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(availability_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(course_fee_bp)

def get_blueprints():
    """
    获取所有蓝图
    
    :return: 蓝图列表
    """
    return [
        auth_bp,
        profile_bp,
        course_bp,
        availability_bp,
        upload_bp,
        teacher_bp,
        course_fee_bp,
    ]

__all__ = ['get_blueprints'] 