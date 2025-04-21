import asyncio

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import traceback
import json

from models.teacher_availability import TeacherAvailability
from forms.availability import AvailabilityBatchForm
from constants import CLASS_DURATION_MINUTES

bp = Blueprint('availability', __name__, url_prefix='/availability')


@bp.route('/list', methods=['GET'])
@login_required
def list_availabilities():
    """显示教师可预约时间列表，使用时间戳进行过滤"""
    try:
        # 获取当前教师
        teacher = current_user

        # -- Read timestamps from query parameters --
        start_timestamp_str = request.args.get('start_timestamp')
        end_timestamp_str = request.args.get('end_timestamp')
        c = request.args.get('c')

        start_timestamp = None
        end_timestamp = None

        try:
            if start_timestamp_str:
                start_timestamp = int(start_timestamp_str)
            if end_timestamp_str:
                end_timestamp = int(end_timestamp_str)
        except (ValueError, TypeError):
            flash('无效的日期参数，请重新选择。', 'warning')
            # Reset timestamps if invalid
            start_timestamp = None
            end_timestamp = None
            # Redirect to avoid keeping invalid params in URL? Maybe just let filter logic handle None.
            # return redirect(url_for('.list_availabilities'))

        # -- End Read timestamps --

        # 基本查询
        query = TeacherAvailability.query.filter_by(teacher_id=teacher.id)

        # 应用搜索条件 (using timestamps)
        if start_timestamp is not None:
            # start_time is stored as UTC timestamp, comparison is direct
            query = query.filter(TeacherAvailability.start_time >= start_timestamp)
            current_app.logger.debug(f"Filtering availability from timestamp: {start_timestamp}")

        if end_timestamp is not None:
            # Filter where the availability *starts* before or at the end timestamp.
            # Since end_timestamp is the end of the day (23:59:59), use <= 
            query = query.filter(TeacherAvailability.start_time <= end_timestamp)
            current_app.logger.debug(f"Filtering availability up to timestamp: {end_timestamp}")

        # 如果没有设置搜索时间，默认不显示已过去的时间
        if start_timestamp is None and end_timestamp is None:
            # Use the provided 'c_timestamp' (local start of day) if available.
            # Otherwise, fall back to the current server UTC time.
            default_start_time = c if c is not None else int(datetime.utcnow().timestamp())

            # Apply the filter using the determined default start time
            query = query.filter(TeacherAvailability.start_time >= default_start_time)
            current_app.logger.debug(f"Default filter: showing availability from timestamp {default_start_time}")

        # 按开始时间排序
        availabilities = query.order_by(TeacherAvailability.start_time).all()

        # 按日期分组
        grouped_availabilities = {}
        for availability in availabilities:
            date_str = availability.get_date_str()
            if date_str not in grouped_availabilities:
                grouped_availabilities[date_str] = []
            grouped_availabilities[date_str].append(availability)

        return render_template('availability/list.html',
                               grouped_availabilities=grouped_availabilities,
                               teacher=teacher,
                               # Pass timestamps back to template for repopulating fields
                               start_timestamp=start_timestamp,
                               end_timestamp=end_timestamp)
    except Exception as e:
        current_app.logger.error(f"获取可预约时间列表失败: {str(e)}\n{traceback.format_exc()}")
        flash('获取可预约时间列表失败，请稍后重试', 'error')
        return redirect(url_for('index'))


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_availability():
    """添加可预约时间"""
    try:
        # 获取当前教师
        teacher = current_user

        # 创建表单
        form = AvailabilityBatchForm()

        if form.validate_on_submit():
            # 检查是否有自定义选择的时间段
            selected_time_slots = request.form.get('selected_time_slots', '')

            if selected_time_slots:
                # 使用前端发送的选择性时间段
                try:
                    time_slots = json.loads(selected_time_slots)
                    time_ranges = [(slot['start_time'], slot['end_time']) for slot in time_slots]
                    current_app.logger.info(
                        f"使用用户选择的时间段 - 教师ID: {teacher.id}, 共 {len(time_ranges)} 个时间段")
                except (json.JSONDecodeError, KeyError) as e:
                    current_app.logger.error(f"解析选择的时间段失败: {str(e)}")
                    flash('解析时间段数据失败，请重试', 'danger')
                    return render_template('availability/add.html', form=form, teacher=teacher,
                                           CLASS_DURATION_MINUTES=CLASS_DURATION_MINUTES)
            else:
                # 获取自动生成的时间范围列表（保持原有逻辑作为备选）
                time_ranges = form.get_datetime_ranges()
                current_app.logger.info(
                    f"使用自动生成的时间段 - 教师ID: {teacher.id}, 生成了 {len(time_ranges)} 个时间段")

            if not time_ranges:
                current_app.logger.warning(f"未能获取有效的时间段 - 教师ID: {teacher.id}")
                flash('无法创建有效的时间段，请检查您的输入。开始时间和结束时间需要至少相差 50 分钟。', 'warning')
                return render_template('availability/add.html', form=form, teacher=teacher,
                                       CLASS_DURATION_MINUTES=CLASS_DURATION_MINUTES)

            # 获取当前时间戳
            current_timestamp = int(datetime.now().timestamp())

            # 过滤掉开始时间小于当前时间的时间段
            valid_time_ranges = []
            for start_time, end_time in time_ranges:
                if start_time < current_timestamp:
                    current_app.logger.warning(
                        f"过滤掉过期时间段 - 教师ID: {teacher.id}, 开始时间: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')}")
                    flash(f'时间段 {datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M")} 至 '
                          f'{datetime.fromtimestamp(end_time).strftime("%H:%M")} '
                          f'的开始时间已过期，已自动跳过', 'warning')
                    continue
                valid_time_ranges.append((start_time, end_time))

            # 更新时间段列表
            time_ranges = valid_time_ranges

            if not time_ranges:
                flash('所有时间段都已过期，无法添加', 'warning')
                return render_template('availability/add.html', form=form, teacher=teacher,
                                       CLASS_DURATION_MINUTES=CLASS_DURATION_MINUTES)

            success_count = 0
            # 检查时间段是否有重复
            for start_time, end_time in time_ranges:
                # 检查当前时间段是否与数据库中的时间段重叠
                overlapping = TeacherAvailability.query.filter(
                    TeacherAvailability.teacher_id == teacher.id,
                    # 重叠条件：(开始时间在已有时间段内) 或 (结束时间在已有时间段内) 或 (已有时间段在新时间段内)
                    ((TeacherAvailability.start_time <= start_time) & (TeacherAvailability.end_time > start_time)) |
                    ((TeacherAvailability.start_time < end_time) & (TeacherAvailability.end_time >= end_time)) |
                    ((TeacherAvailability.start_time >= start_time) & (TeacherAvailability.end_time <= end_time))
                ).first()

                if overlapping:
                    # 找到重叠时间段，跳过此时间段但继续处理其他时间段
                    overlap_start = datetime.fromtimestamp(overlapping.start_time)
                    overlap_end = datetime.fromtimestamp(overlapping.end_time)
                    current_app.logger.warning(
                        f"时间段重叠 - 教师ID: {teacher.id}, "
                        f"新时间段: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M')} 至 {datetime.fromtimestamp(end_time).strftime('%H:%M')}, "
                        f"已有时间段: {overlap_start.strftime('%Y-%m-%d %H:%M')} 至 {overlap_end.strftime('%H:%M')}"
                    )
                    flash(f'时间段 {datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M")} 至 '
                          f'{datetime.fromtimestamp(end_time).strftime("%H:%M")} '
                          f'与已有时间段重叠，已自动跳过', 'warning')
                    continue

                # 保存非重叠的时间段
                availability = TeacherAvailability(
                    teacher_id=teacher.id,
                    start_time=start_time,
                    end_time=end_time
                )
                availability.save()
                success_count += 1

            if success_count > 0:
                flash(f'成功添加 {success_count} 个可预约时间段', 'success')
                return redirect(url_for('availability.list_availabilities'))
            else:
                flash('所有时间段都与已有时间段重叠，未能添加任何新时间段', 'warning')
                return render_template('availability/add.html', form=form, teacher=teacher,
                                       CLASS_DURATION_MINUTES=CLASS_DURATION_MINUTES)

        return render_template('availability/add.html', form=form, teacher=teacher,
                               CLASS_DURATION_MINUTES=CLASS_DURATION_MINUTES)
    except Exception as e:
        current_app.logger.error(f"添加可预约时间失败: {str(e)}\n{traceback.format_exc()}")
        flash('添加可预约时间失败，请稍后重试', 'error')
        return redirect(url_for('availability.list_availabilities'))


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_availability(id):
    """删除可预约时间"""
    try:
        # 获取当前教师
        teacher = current_user

        # 根据ID查找可预约时间
        availability = TeacherAvailability.query.filter_by(id=id, teacher_id=teacher.id).first_or_404()

        # 检查是否已被预约
        if availability.is_booked():
            return jsonify({'success': False, 'message': '该时间段已被预约，无法删除'})

        # 检查是否已过期
        if availability.is_expired():
            current_app.logger.warning(f"尝试删除过期时间段 - 教师ID: {teacher.id}, 时间段ID: {id}")
            return jsonify({'success': False, 'message': '该时间段已过期，无法删除'})

        # 删除可预约时间
        availability.delete()

        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        current_app.logger.error(f"删除可预约时间失败: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': '删除失败，请稍后重试'})
