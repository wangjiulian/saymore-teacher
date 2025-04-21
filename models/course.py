from extensions import db
from datetime import datetime, timezone, timedelta
from enum import Enum
from models.student import Student
from models.subject import Subject
from models.teacher import Teacher


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


class CourseStatus(Enum):
    NOT_STARTED = 1  # 未开始
    IN_PROGRESS = 2  # 上课中
    COMPLETED = 3  # 已完成
    CANCELLED = 4  # 已取消


class CourseType(Enum):
    REGULAR = 1  # 正式课
    TRIAL = 2  # 试听课


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='课程ID')
    course_type = db.Column(db.SmallInteger, nullable=False, default=1, comment='课程类型：1-正式课，2-试听课')
    name = db.Column(db.String(100), nullable=False, default='', comment='课程名称')
    subject_id = db.Column(db.Integer, nullable=False, default=0, index=True, comment='学科ID')
    teacher_id = db.Column(db.Integer, nullable=False, default=0, index=True, comment='老师ID')
    student_id = db.Column(db.Integer, nullable=False, default=0, index=True, comment='学生ID')
    status = db.Column(db.SmallInteger, nullable=False, default=0,
                       comment='上课状态：1-待上课，2-上课中，3-已完成，4-已取消')
    cancel_reason = db.Column(db.String(255), nullable=False, default='', comment='取消原因')
    start_time = db.Column(db.Integer, nullable=False, comment='课程开始时间（Unix时间戳，单位：秒）')
    end_time = db.Column(db.Integer, nullable=False, comment='课程结束时间（Unix时间戳，单位：秒）')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # 关系定义
    student = db.relationship('Student', foreign_keys=[student_id],
                              primaryjoin="Course.student_id == Student.id",
                              backref=db.backref('courses', lazy='dynamic'))

    teacher = db.relationship('Teacher', foreign_keys=[teacher_id],
                              primaryjoin="Course.teacher_id == Teacher.id",
                              backref=db.backref('courses', lazy='dynamic'))

    subject = db.relationship('Subject', foreign_keys=[subject_id],
                              primaryjoin="Course.subject_id == Subject.id",
                              backref=db.backref('courses', lazy='dynamic'))

    def __repr__(self):
        return f'<Course {self.id}>'

    def get_duration_minutes(self):
        """获取课程时长（分钟）"""
        if not self.start_time or not self.end_time:
            return 0
        return (self.end_time - self.start_time) // 60

    # def get_formatted_time(self):
    #     """获取格式化的上课时间段"""
    #     if not self.start_time or not self.end_time:
    #         return "时间未设置"
    #
    #     start_dt = datetime.fromtimestamp(self.start_time)
    #     end_dt = datetime.fromtimestamp(self.end_time)
    #     return f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}"

    def get_status_text(self):
        """获取状态文本"""
        status_map = {
            CourseStatus.NOT_STARTED.value: "待上课",
            CourseStatus.IN_PROGRESS.value: "上课中",
            CourseStatus.COMPLETED.value: "已完成",
            CourseStatus.CANCELLED.value: "已取消"
        }
        return status_map.get(self.status, "未知状态")

    def get_course_type_text(self):
        """获取课程类型文本"""
        type_map = {
            CourseType.REGULAR.value: "正式课",
            CourseType.TRIAL.value: "试听课"
        }
        return type_map.get(self.course_type, "未知类型")

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'course_type': self.course_type,
            'course_type_text': self.get_course_type_text(),
            'name': self.name,
            'subject_id': self.subject_id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'status': self.status,
            'status_text': self.get_status_text(),
            'cancel_reason': self.cancel_reason,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'student_name': self.student.nickname if self.student else "",
            'teacher_name': self.teacher.name if self.teacher else "",
            'subject_name': self.subject.name if self.subject else "",
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
