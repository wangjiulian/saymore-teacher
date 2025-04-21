from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, Response
from flask_login import login_required, current_user
# from sqlalchemy.orm import joinedload # Removed joinedload as direct relationship isn't defined
from extensions import db
from models import TeacherCourseFee, Student, Course, Subject
from datetime import datetime, timezone
import io
import csv
import logging

bp = Blueprint('course_fee', __name__, url_prefix='/course-fees')
logger = logging.getLogger(__name__)


@bp.route('/')
@login_required
def list_fees():
    """课时记录列表页面"""
    page = request.args.get('page', 1, type=int)
    # Read timestamps directly from args - frontend sends these
    start_timestamp = request.args.get('start_timestamp', type=int)
    end_timestamp = request.args.get('end_timestamp', type=int)
    logger.info(f"Received timestamp filter: start_timestamp={start_timestamp}, end_timestamp={end_timestamp}")

    # 构建基础查询，只查询当前老师的记录
    # Join with Student table to get student details
    query = db.session.query(
        TeacherCourseFee, Student.nickname
    ).select_from(TeacherCourseFee).join(
        Student, TeacherCourseFee.student_id == Student.id
    ).filter(TeacherCourseFee.teacher_id == current_user.id)

    # 处理日期范围查询 (Using provided timestamps directly)
    if start_timestamp is not None:
        query = query.filter(TeacherCourseFee.created_at >= start_timestamp)
        logger.info(f"Applied start_timestamp filter: {start_timestamp}")

    if end_timestamp is not None:
        query = query.filter(TeacherCourseFee.created_at <= end_timestamp)
        logger.info(f"Applied end_timestamp filter: {end_timestamp}")

    # 按创建时间降序排序
    query = query.order_by(TeacherCourseFee.created_at.desc())

    # 分页
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    # Since we are selecting specific columns, paginate needs the query object directly
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    # Results are tuples: (TeacherCourseFee object, student_nickname)
    fees_with_students = pagination.items

    return render_template(
        'course_fee/list.html',
        fees_with_students=fees_with_students,
        pagination=pagination,
        # Pass timestamps back for pagination links and JS repopulation
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp
        # Do NOT pass start_date/end_date strings
    )


@bp.route('/export')
@login_required
def export_fees():
    """获取课时记录数据用于导出"""
    # Read timestamps directly from args for filtering
    start_timestamp = request.args.get('start_timestamp', type=int)
    end_timestamp = request.args.get('end_timestamp', type=int)
    logger.info(
        f"Export request with timestamp filter: start_timestamp={start_timestamp}, end_timestamp={end_timestamp}")

    # 构建基础查询，加入 Course 和 Subject 表
    query = db.session.query(
        TeacherCourseFee,
        Student.nickname,
        Course.name.label('course_name'),
        Course.start_time.label('course_start_time'),
        Course.end_time.label('course_end_time'),
        Subject.name.label('subject_name')
    ).join(Student, TeacherCourseFee.student_id == Student.id) \
        .join(Course, TeacherCourseFee.course_id == Course.id) \
        .outerjoin(Subject, Course.subject_id == Subject.id) \
        .filter(TeacherCourseFee.teacher_id == current_user.id)

    # 处理日期范围查询 (Using provided timestamps directly)
    if start_timestamp is not None:
        query = query.filter(TeacherCourseFee.created_at >= start_timestamp)
        logger.info(f"Export: Applying start_timestamp filter: {start_timestamp}")

    if end_timestamp is not None:
        query = query.filter(TeacherCourseFee.created_at <= end_timestamp)
        logger.info(f"Export: Applying end_timestamp filter: {end_timestamp}")

    # 按创建时间降序排序
    query = query.order_by(TeacherCourseFee.created_at.desc())

    # 获取所有符合条件的记录（不分页）
    # Results are now tuples: (TeacherCourseFee, student_nickname, course_name, course_start_time, course_end_time, subject_name)
    all_fees_with_details = query.all()

    # Prepare data for JSON response
    data_to_export = []
    # Adjust loop variable unpacking
    index = 0
    for fee, student_nickname, course_name, course_start_time, course_end_time, subject_name in all_fees_with_details:
        index += 1  # Increment index for each record+
        fee_type_text = '正常结算' if fee.type == 1 else ('课时补偿' if fee.type == 2 else '未知')
        data_to_export.append({
            'id': index,
            'student_name': student_nickname if student_nickname else '未知学生',
            'course_name': course_name if course_name else 'N/A',  # Add course name
            'subject_name': subject_name if subject_name else '未设置',  # Add subject name
            'course_start_time': course_start_time,  # Add course start time timestamp
            'course_end_time': course_end_time,  # Add course end time timestamp
            'title': fee.title,  # Keep original fee title if needed, or remove if course_name is sufficient
            'hours': fee.hours,
            'fees': fee.fees,
            'type': fee_type_text,
            'remark': fee.remark if fee.remark else '-',
            'created_at_timestamp': fee.created_at
        })

    logger.info(f"Returning {len(data_to_export)} records for export.")
    return jsonify({'success': True, 'data': data_to_export})
