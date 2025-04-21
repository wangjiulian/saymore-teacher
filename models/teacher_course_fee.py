from extensions import db
from datetime import datetime, timezone
from enum import Enum


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


class TeacherCourseFeeType(Enum):
    NORMAL = 1
    COMPENSATION = 2


class TeacherCourseFee(db.Model):
    __tablename__ = 'teacher_course_fees'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.BigInteger, nullable=False, default=0)
    course_id = db.Column(db.BigInteger, nullable=False, default=0)
    student_id = db.Column(db.BigInteger, nullable=False, default=0)
    student_package_id = db.Column(db.BigInteger, nullable=False, default=0)
    title = db.Column(db.String(255), nullable=False, default='')
    hours = db.Column(db.Float, nullable=False, default=0)
    fees = db.Column(db.Float, nullable=False, default=0)
    type = db.Column(db.Integer, nullable=False, default=0, comment='课时费类型：1 正常结算 2 课时补偿')
    remark = db.Column(db.String(255), nullable=False, default='')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<TeacherCourseFee %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'course_id': self.course_id,
            'student_id': self.student_id,
            'student_package_id': self.student_package_id,
            'title': self.title,
            'hours': self.hours,
            'fees': self.fees,
            'remark': self.remark,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
