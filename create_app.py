import flask
from flask import Flask, redirect, url_for, render_template, Response
from config import Config
from extensions import db, login_manager, migrate
from flask_login import current_user

from models.subject import Subject
from flask_wtf.csrf import CSRFProtect, CSRFError
from datetime import datetime
from routes import init_app


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # 初始化 CSRF 保护
    csrf = CSRFProtect(app)

    # 设置CSRF豁免路由（如果需要）
    # csrf.exempt(bp_name)

    # CSRF错误处理
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        app.logger.error(f"CSRF错误: {e.description}")
        return render_template('errors/csrf_error.html', reason=e.description), 400

    # 根路由重定向到个人资料页面或登录页面，取决于登录状态
    @app.route('/',methods=["GET", "HEAD"])
    def index():
        if flask.request.method == "HEAD":
            return Response(status=200)  # 直接返回 200 OK，不进行重定向
        
        # 检查用户是否已登录，如果未登录则重定向到登录页面
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return redirect(url_for('profile.index'))

    # 注册所有蓝图

    init_app(app)

    # 添加 now 函数和获取父科目函数到 Jinja2 环境
    @app.context_processor
    def utility_processor():
        def get_parent_subject(parent_id):
            if parent_id:
                return Subject.query.get(parent_id)
            return None

        return dict(
            now=datetime.now,
            get_parent_subject=get_parent_subject
        )

    # 添加请求结束后自动关闭数据库会话的钩子
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
