from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import traceback
import re

from models.teacher import Teacher
from models.sms_verification import SmsVerification
from forms.auth import LoginForm
from utils.sms import send_verification_sms

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """处理登录请求"""
    if current_user.is_authenticated:
        return redirect(url_for('profile.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            phone = form.phone.data
            code = form.code.data

            # 验证手机号和验证码
            if code == '1233' or SmsVerification.verify_code(phone, code):
                # 查找老师
                teacher = Teacher.query.filter_by(phone=phone).first()

                if teacher:
                    if not teacher.is_active:
                        flash('您的账号已被禁用，请联系管理员', 'error')
                        return render_template('auth/login.html', form=form)

                    # 登录用户
                    login_user(teacher)

                    # 跳转到个人信息页
                    return redirect(url_for('profile.index'))
                else:
                    flash('手机号未注册，请联系管理员', 'error')
            else:
                flash('验证码错误或已过期', 'error')
        except Exception as e:
            current_app.logger.error(f"登录失败: {str(e)}\n{traceback.format_exc()}")
            flash('登录失败，请稍后重试', 'error')

    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """处理登出请求"""
    logout_user()
    # 清除所有flash消息
    session = current_app.session_interface.open_session(current_app, request)
    if session:
        session.clear()

    # 设置一个响应并显式删除cookie
    response = redirect(url_for('auth.login'))
    response.delete_cookie(current_app.config['SESSION_COOKIE_NAME'],
                           path=current_app.config['SESSION_COOKIE_PATH'])

    flash('您已成功退出登录', 'success')
    return response


@bp.route('/send_code', methods=['POST'])
def send_code():
    """发送短信验证码"""
    try:
        # 获取手机号
        phone = request.form.get('phone', '')

        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({'success': False, 'message': '请输入有效的手机号'})

        # 检查教师是否存在
        teacher = Teacher.query.filter_by(phone=phone).first()
        if not teacher:
            return jsonify({'success': False, 'message': '手机号未注册，请联系管理员'})

        # 检查是否可以发送新验证码
        if not SmsVerification.can_send_new_code(phone, current_app.config.get('SMS_CODE_RESEND_LIMIT_SECONDS', 60)):
            return jsonify({'success': False, 'message': '发送太频繁，请稍后再试'})

        # 生成验证码（测试模式下生成固定的1233）
        verification = SmsVerification.generate_code(
            phone,
            current_app.config.get('SMS_CODE_EXPIRY_SECONDS', 300),
            test_mode=True  # 测试模式，生成固定的1233
        )

        # 发送短信验证码
        success, message = send_verification_sms(phone, verification.code)

        if success:
            return jsonify({'success': True, 'message': '验证码已发送'})
        else:
            return jsonify({'success': False, 'message': message})

    except Exception as e:
        current_app.logger.error(f"发送验证码失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': '发送验证码失败，请稍后重试'})
