from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import traceback

from models.teacher import Teacher
from models.subject import Subject
from forms.teacher import TeacherProfileForm

bp = Blueprint('teacher', __name__)


@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """显示教师个人资料"""
    try:
        # 使用当前登录的教师信息
        teacher = current_user
        
        return render_template('teacher/profile.html', teacher=teacher)
    except Exception as e:
        current_app.logger.error(f"获取教师资料失败: {str(e)}\n{traceback.format_exc()}")
        flash('获取教师资料失败，请稍后重试', 'error')
        return redirect(url_for('index'))


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑教师个人资料"""
    try:
        # 获取当前登录的教师
        teacher = current_user
        
        # 创建表单，并使用教师数据进行预填充
        form = TeacherProfileForm(obj=teacher)
        
        # 设置表单的选中学科
        if request.method == 'GET':
            if teacher.subjects.count() > 0:
                form.subjects.data = [subject.id for subject in teacher.subjects]
        
        if form.validate_on_submit():
            # 更新教师基本信息，但不包括subjects字段
            # 创建一个排除subjects的字段列表
            exclude_fields = ['subjects', 'submit']
            for field_name, field in form._fields.items():
                if field_name not in exclude_fields:
                    field.populate_obj(teacher, field_name)
            
            # 单独处理学科关联
            teacher.subjects = []
            selected_subjects = Subject.query.filter(Subject.id.in_(form.subjects.data)).all()
            for subject in selected_subjects:
                teacher.subjects.append(subject)
                
            teacher.updated_at = datetime.now().timestamp()
            teacher.save()
            
            flash('个人资料更新成功', 'success')
            return redirect(url_for('teacher.profile'))
            
        return render_template('teacher/edit_profile.html', form=form, teacher=teacher)
    except Exception as e:
        current_app.logger.error(f"编辑教师资料失败: {str(e)}\n{traceback.format_exc()}")
        flash('编辑教师资料失败，请稍后重试', 'error')
        return redirect(url_for('teacher.profile')) 