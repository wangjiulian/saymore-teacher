from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class LoginForm(FlaskForm):
    """
    登录表单 - 使用手机号和验证码登录
    """
    phone = StringField('手机号', validators=[
        DataRequired(message='请输入手机号'),
        Length(min=11, max=11, message='手机号必须为11位'),
        Regexp(r'^1[3-9]\d{9}$', message='请输入有效的手机号')
    ])
    code = StringField('验证码', validators=[
        DataRequired(message='请输入验证码'),
        Length(min=4, max=6, message='验证码长度为4-6位')
    ])
    submit = SubmitField('登录') 