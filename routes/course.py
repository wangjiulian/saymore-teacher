from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime, timezone
import logging

import constants
from extensions import db
from models import (
    Course, CourseOperationLog, Subject, Teacher, Student, TeacherCourseFee, StudentTeacherPackage,
    AdminUser, StudentPackageDetail, StudentPackage, StudentTrialQuota, TeacherCompensationCourse,
    TeacherCompensationCourseLog, TeacherAvailability
)

from models.course import (CourseStatus, CourseType)
from models.student_package_detail import (ChangeType, Change)
from models.teacher_compensation_course_log import TeacherCompensationCourseLogType
from models.teacher_course_fee import TeacherCourseFeeType

bp = Blueprint('course', __name__, url_prefix='/courses')
logger = logging.getLogger(__name__)


@bp.route('/')
@login_required
def index():
    """Course list page"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=int)
    student_name = request.args.get('student_name', '')
    course_id_highlight = request.args.get('course_id_highlight', type=int)
    course_type = request.args.get('course_type', type=int)
    # Read timestamps directly from args - frontend sends these
    start_timestamp = request.args.get('start_timestamp', type=int)
    end_timestamp = request.args.get('end_timestamp', type=int)
    logger.info(f"Received timestamp filter: start_timestamp={start_timestamp}, end_timestamp={end_timestamp}")

    # Build query
    query = Course.query.filter(Course.teacher_id == current_user.id)
    if course_id_highlight is not None:
        query = query.filter(Course.id == course_id_highlight)
    # Filter by status
    if status:
        query = query.filter(Course.status == status)

    # Filter by course type
    if course_type:
        query = query.filter(Course.course_type == course_type)

    # Filter by date range (Using provided timestamps directly)
    if start_timestamp is not None:
        query = query.filter(Course.start_time >= start_timestamp)
        logger.info(f"Applied start_timestamp filter: {start_timestamp}")

    if end_timestamp is not None:
        query = query.filter(Course.start_time <= end_timestamp)
        logger.info(f"Applied end_timestamp filter: {end_timestamp}")

    # Filter by student name
    if student_name:
        student_ids = Student.query.filter(
            or_(
                Student.nickname.like(f'%{student_name}%'),
                Student.phone.like(f'%{student_name}%')
            )
        ).with_entities(Student.id).all()

        student_ids = [s[0] for s in student_ids]
        if student_ids:
            query = query.filter(Course.student_id.in_(student_ids))
        else:
            # Return empty results, pass back filters for consistency
            return render_template(
                'course/list.html',
                courses=[],
                pagination=None,
                status=status,
                student_name=student_name,
                course_type=course_type,
                start_timestamp=start_timestamp,  # Pass back for pagination/JS repopulation
                end_timestamp=end_timestamp  # Pass back for pagination/JS repopulation
            )

    # Sorting: Pending and in-progress courses by start time ascending, completed courses by start time descending
    query = query.order_by(
        # Pending and in-progress first
        Course.status.in_([1, 2]).desc(),
        # Pending and in-progress (status=1 or 2) by start time ascending
        db.case(
            (Course.status.in_([1, 2]), Course.start_time),
            else_=0
        ).asc(),
        # Completed and canceled by start time descending
        db.case(
            (Course.status.in_([3, 4]), Course.start_time),
            else_=0
        ).desc()
    )

    # Pagination
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    courses = pagination.items

    return render_template(
        'course/list.html',
        courses=courses,
        pagination=pagination,
        status=status,
        student_name=student_name,
        course_id_highlight=course_id_highlight,
        course_type=course_type,
        # Pass timestamps back for pagination links and JS repopulation
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp
        # Do NOT pass start_date/end_date strings
    )


@bp.route('/<int:course_id>/start', methods=['POST'])
@login_required
def start_course(course_id):
    """Start class"""
    course = Course.query.get_or_404(course_id)

    # Verify course belongs to current teacher
    if course.teacher_id != current_user.id:
        flash('You are not the teacher for this course', 'warning')
        flash('Only pending classes can be started', 'warning')
        return jsonify({'success': False, 'message': 'You are not the teacher for this course'})

    # Verify course status
    if course.status != 1:  # Not pending
        flash('Only pending classes can be started', 'warning')
        return jsonify({'success': False, 'message': 'Only pending classes can be started'})

    if course.start_time - int(datetime.now().timestamp()) > constants.CLASS_START_TIME_BUFFER_MINUTES:
        flash('Class can only be started 5 minutes before the scheduled time', 'warning')
        return jsonify({'success': False, 'message': 'Class can only be started 5 minutes before the scheduled time'})

    try:
        # Record original status
        old_status = course.status

        # Update course status
        course.status = 2  # In progress

        # Record operation log
        log = CourseOperationLog(
            course_id=course.id,
            operator_id=current_user.id,
            operator_type=2,  # Teacher
            old_status=old_status,
            new_status=course.status,
            operation_time=datetime.now().timestamp()
        )

        db.session.add(log)
        db.session.commit()

        flash('Class started successfully', 'success')

        return jsonify({
            'success': True,
            'message': 'Class started',
            'new_status': course.status,
            'new_status_text': course.get_status_text()
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to start class: {str(e)}")
        return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'})


@bp.route('/<int:course_id>/finish', methods=['POST'])
@login_required
def finish_course(course_id):
    """End class"""
    course = Course.query.get_or_404(course_id)

    # Verify course belongs to current teacher
    if course.teacher_id != current_user.id:
        flash('You are not the teacher for this course', 'error')
        return jsonify({'success': False, 'message': 'You are not the teacher for this course'})

    # Verify course status
    if course.status != CourseStatus.IN_PROGRESS.value:  # Not in progress
        flash('Only in-progress classes can be ended', 'error')
        return jsonify({'success': False, 'message': 'Only in-progress classes can be ended'})

    if course.end_time > int(datetime.now().timestamp()):
        flash('Class end time has not been reached yet', 'error')
        return jsonify({'success': False, 'message': 'Class end time has not been reached yet'})

    try:
        # Record original status
        old_status = course.status

        # Record operation log
        log = CourseOperationLog(
            course_id=course.id,
            operator_id=current_user.id,
            operator_type=2,  # Teacher
            old_status=old_status,
            new_status=course.status,
            operation_time=datetime.now().timestamp()
        )
        db.session.add(log)

        # Update course status
        rows_updated = Course.query.filter_by(id=course_id, status=2).update({
            'status': CourseStatus.COMPLETED.value
        })
        if rows_updated == 0:
            flash('Course status update failed', 'error')
            return jsonify({'success': False, 'message': 'Course status update failed'})
        if course.course_type == CourseType.REGULAR.value:
            # Regular course
            # Get package consumption info
            student_package_detail = StudentPackageDetail.query.filter_by(
                course_id=course_id
            ).first()
            if student_package_detail is None:
                flash('Course package consumption information does not exist', 'error')
                return jsonify({'success': False, 'message': 'Course package consumption information does not exist'})

            hours = student_package_detail.hours

            # Check if teacher has compensation hours to use
            teacher_compensation = TeacherCompensationCourse.query.filter_by(
                teacher_id=current_user.id,
                student_id=course.student_id
            ).first()

            # Check if teacher has compensation hours and if they have enough for this class
            if teacher_compensation is not None and teacher_compensation.left_hours >= hours:
                # Update teacher compensation hours
                teacher_compensation.left_hours -= hours
                # Add new compensation record
                teacher_compensation_log = TeacherCompensationCourseLog(
                    teacher_id=current_user.id,
                    student_id=course.student_id,
                    course_id=course_id,
                    hours=hours,
                    type=TeacherCompensationCourseLogType.USE_COMPENSATION.value,  # Use compensation
                )
                db.session.add(teacher_compensation_log)

                # Add course fee record, marked as compensation
                teacher_course_fee = TeacherCourseFee(
                    teacher_id=current_user.id,
                    course_id=course_id,
                    student_id=course.student_id,
                    student_package_id=student_package_detail.student_package_id,
                    title=student_package_detail.title,
                    hours=hours,
                    fees=0,  # No fee for compensation hours
                    type=TeacherCourseFeeType.COMPENSATION.value,
                    remark='Compensation Hours'
                )
                db.session.add(teacher_course_fee)
            else:
                # Get teacher's fee for this package
                student_teacher_package = StudentTeacherPackage.query.filter_by(
                    teacher_id=current_user.id,
                    student_package_id=student_package_detail.student_package_id
                ).first()
                if student_teacher_package is None:
                    flash('Teacher package fee information does not exist', 'error')
                    return jsonify({'success': False, 'message': 'Teacher package fee information does not exist'})

                fees = student_teacher_package.price

                # Total course fee
                total_fees = hours * fees

                # Record teacher course fee
                teacher_course_fee = TeacherCourseFee(
                    teacher_id=current_user.id,
                    course_id=course_id,
                    student_id=course.student_id,
                    student_package_id=student_package_detail.student_package_id,
                    title=course.name,
                    hours=hours,
                    fees=total_fees,
                    type=TeacherCourseFeeType.NORMAL.value,
                )
                db.session.add(teacher_course_fee)

        # Update teacher teaching hours
        consumed_hours = (course.end_time - course.start_time) / 3000  # 50 minutes per class
        rows_updated_teacher = Teacher.query.filter_by(id=current_user.id).update({
            'course_hours': Teacher.course_hours + consumed_hours
        })
        if rows_updated_teacher == 0:
            flash('Failed to update teacher course hours', 'error')
            return jsonify({'success': False, 'message': 'Failed to update teacher course hours'})
        db.session.commit()

        flash('Class ended successfully', 'success')

        return jsonify({
            'success': True,
            'message': 'Class ended',
            'new_status': course.status,
            'new_status_text': course.get_status_text()
        })

    except Exception as e:
        db.session.rollback()
        flash('Failed to end class', 'error')
        current_app.logger.error(f"Failed to end class: {str(e)}")
        return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'})


@bp.route('/<int:course_id>/cancel', methods=['POST'])
@login_required
def cancel_course(course_id):
    # Get UTC timestamp as integer
    currentTime = int(datetime.now(timezone.utc).timestamp())
    """Cancel class"""
    course = Course.query.get_or_404(course_id)

    # Verify course belongs to current teacher
    if course.teacher_id != current_user.id:
        flash('You are not the teacher for this course', 'error')
        return jsonify({'success': False, 'message': 'You are not the teacher for this course'})

    # Verify course status
    if course.status not in [CourseStatus.NOT_STARTED.value, CourseStatus.IN_PROGRESS.value]:  # Not pending or in progress
        flash('Only pending or in-progress classes can be canceled', 'error')
        return jsonify({'success': False, 'message': 'Only pending or in-progress classes can be canceled'})

    # Get cancellation reason
    reason = request.json.get('reason', '')
    if not reason:
        flash('Please provide a reason for cancellation', 'error')
        return jsonify({'success': False, 'message': 'Please provide a reason for cancellation'})

    # Add prefix
    prefixed_reason = f"Teacher cancellation: {reason}"

    try:
        # Record original status
        old_status = course.status

        # Update course status and cancellation reason
        course.status = CourseStatus.CANCELLED.value  # Cancelled
        course.cancel_reason = prefixed_reason

        if course.course_type == 1:  # Regular course
            # When teacher cancels, return all course hours to student
            # Get package consumption info
            student_package_detail = StudentPackageDetail.query.filter_by(
                course_id=course_id
            ).first()
            if student_package_detail is None:
                flash('Course package consumption information does not exist', 'error')
                return jsonify({'success': False, 'message': 'Course package consumption information does not exist'})

            hours = student_package_detail.hours

            studentPackage = StudentPackage.query.get_or_404(student_package_detail.student_package_id)
            if studentPackage is None:
                flash('Student course package does not exist', 'error')
                return jsonify({'success': False, 'message': 'Student course package does not exist'})

            # Return hours to student package
            up_student_package_rows = StudentPackage.query.filter_by(
                id=student_package_detail.student_package_id, left_hours=studentPackage.left_hours).update({
                'left_hours': StudentPackage.left_hours + hours,
                'updated_at': currentTime,
            })
            if up_student_package_rows == 0:
                flash('Data has been updated, please try again', 'error')
                return jsonify({'success': False, 'message': 'Data has been updated, please try again'})

            # Add record of returned hours
            add_student_package_detail = StudentPackageDetail(
                student_id=course.student_id,
                student_package_id=student_package_detail.student_package_id,
                course_id=course_id,
                title=f"Cancel {student_package_detail.title}",
                hours=hours,
                left_hours=studentPackage.left_hours,
                change=Change.ADD.value,
                change_type=ChangeType.CANCEL_NO_RESPONSIBILITY.value,
                created_at=currentTime,
                updated_at=currentTime
            )
            db.session.add(add_student_package_detail)

            #  If canceled more than 1 hour before, no teacher responsibility. Within 1 hour, teacher gives 1 free hour
            if course.start_time - currentTime < constants.NO_RESPONSIBILITY_CANCEL_TIME_INTERVAL:
                # Give student 1 extra hour
                compensationHours = 1
                # Update student package with extra hour
                up_extra_student_package_rows = StudentPackage.query.filter_by(
                    id=student_package_detail.student_package_id, left_hours=studentPackage.left_hours).update({
                    'left_hours': StudentPackage.left_hours + compensationHours,
                    'updated_at': currentTime,
                })
                if up_extra_student_package_rows == 0:
                    flash('Data has been updated, please try again', 'error')
                    return jsonify({'success': False, 'message': 'Data has been updated, please try again'})

                # Add record of compensation hours
                add_extra_student_package_detail = StudentPackageDetail(
                    student_id=course.student_id,
                    student_package_id=student_package_detail.student_package_id,
                    course_id=course_id,
                    title=f"Teacher cancellation compensation",
                    hours=compensationHours,
                    left_hours=studentPackage.left_hours,
                    change=Change.ADD.value,
                    change_type=ChangeType.CANCEL_NO_RESPONSIBILITY.value,
                    created_at=currentTime,
                    updated_at=currentTime
                )
                db.session.add(add_extra_student_package_detail)

                # Update total package hours
                up_student_package_rows = StudentPackage.query.filter_by(
                    id=student_package_detail.student_package_id, hours=StudentPackage.hours).update({
                    'hours': StudentPackage.hours + compensationHours,
                    'updated_at': currentTime,
                })

                # Record compensation hours log
                compensationLog = TeacherCompensationCourseLog(
                    teacher_id=current_user.id,
                    student_id=course.student_id,
                    course_id=course_id,
                    hours=compensationHours,
                    type=TeacherCompensationCourseLogType.COMPENSATION.value,
                    created_at=currentTime,
                    updated_at=currentTime
                )

                db.session.add(compensationLog)

                # Update teacher compensation hours total
                teacherCompensationCourse = TeacherCompensationCourse.query.filter_by(
                    teacher_id=current_user.id, student_id=course.student_id).first()
                if teacherCompensationCourse is None:
                    teacherCompensationCourse = TeacherCompensationCourse(
                        teacher_id=current_user.id,
                        student_id=course.student_id,
                        total_hours=compensationHours,
                        left_hours=compensationHours,
                        created_at=currentTime,
                        updated_at=currentTime
                    )
                    db.session.add(teacherCompensationCourse)
                else:
                    TeacherCompensationCourse.query.filter_by(
                        teacher_id=current_user.id, student_id=course.student_id
                    ).update({
                        'total_hours': teacherCompensationCourse.total_hours + compensationHours,
                        'left_hours': teacherCompensationCourse.left_hours + compensationHours,
                        'updated_at': currentTime
                    })

        else:  # Trial course
            # Return student's trial opportunity
            up_student_trial_quota_rows = StudentTrialQuota.query.filter_by(
                student_id=course.student_id,
                course_id=course_id
            ).update({
                'course_id': 0,
                'updated_at': currentTime,
            })
            if up_student_trial_quota_rows == 0:
                flash('Failed to update student trial quota', 'error')
                return jsonify({'success': False, 'message': 'Failed to update student trial quota'})

        # Record operation log
        log = CourseOperationLog(
            course_id=course.id,
            operator_id=current_user.id,
            operator_type=2,  # Teacher
            old_status=old_status,
            new_status=course.status,
            operation_time=currentTime,
            cancel_reason=prefixed_reason,
            created_at=currentTime,
            updated_at=currentTime,
        )

        # Free up teacher availability
        up_teacher_availability_rows = TeacherAvailability.query.filter_by(teacher_id=current_user.id,
                                                                           course_id=course_id).update({
            'course_id': 0
        })
        if up_teacher_availability_rows == 0:
            flash('Failed to update teacher availability', 'error')
            return jsonify({'success': False, 'message': 'Failed to update teacher availability'})

        db.session.add(log)
        db.session.commit()

        flash('Course canceled successfully', 'success')

        return jsonify({
            'success': True,
            'message': 'Course canceled',
            'new_status': course.status,
            'new_status_text': course.get_status_text()
        })

    except Exception as e:
        db.session.rollback()
        flash("Failed to cancel course", 'error')
        current_app.logger.error(f"Failed to cancel course: {str(e)}")
        return jsonify({'success': False, 'message': f'Operation failed: {str(e)}'})


@bp.route('/<int:course_id>/logs')
@login_required
def course_logs(course_id):
    """获取课程操作日志"""
    course = Course.query.get_or_404(course_id)

    # 验证课程是否属于当前教师
    if course.teacher_id != current_user.id:
        flash('You are not the teacher for this course', 'error')
        return jsonify({'success': False, 'message': 'You are not the teacher for this course'})

    logs = CourseOperationLog.query.filter_by(course_id=course_id).order_by(
        CourseOperationLog.operation_time.desc()).all()

    # 获取操作者信息
    logs_with_operator = []
    for log in logs:
        log_dict = log.to_dict()

        # 为老师类型的操作者添加名称
        if log.operator_type == 2:  # 老师

            operator = Teacher.query.get(log.operator_id)
            if operator:
                log_dict['operator_name'] = operator.name
            else:
                log_dict['operator_name'] = f"Unknown teacher (ID:{log.operator_id})"
        # 为学生类型的操作者添加名称
        elif log.operator_type == 3:  # 学生
            operator = Student.query.get(log.operator_id)
            if operator:
                log_dict['operator_name'] = operator.nickname
            else:
                log_dict['operator_name'] = f"Unknown student (ID:{log.operator_id})"
        # 为教务老师类型的操作者添加名称
        elif log.operator_type == 1:  # 教务老师
            operator = AdminUser.query.get(log.operator_id)
            # 这里根据实际情况获取教务老师信息
            log_dict['operator_name'] = operator.name
        else:
            log_dict['operator_name'] = f"Unknown admin teacher (ID:{log.operator_id})"

        logs_with_operator.append(log_dict)

    # 获取学生和科目信息
    student_name = course.student.nickname if course.student else "Unknown student"
    subject_info = ""
    if course.subject:
        # 获取科目大类
        parent_subject = None
        if course.subject.parent_id:
            parent_subject = Subject.query.get(course.subject.parent_id)

        if parent_subject:
            subject_info = f"{parent_subject.name} - {course.subject.name}"
        else:
            subject_info = course.subject.name
    else:
        subject_info = "Unknown subject"

    return jsonify({
        'success': True,
        'course': {
            'id': course.id,
            'name': course.name,
            'course_type_text': course.get_course_type_text(),
            'status_text': course.get_status_text(),
            'student_name': student_name,
            'subject_info': subject_info,
            'start_time': course.start_time,
            'end_time': course.end_time,
            # 'formatted_time': course.get_formatted_time(),
            'cancel_reason': course.cancel_reason
        },
        'logs': logs_with_operator
    })
