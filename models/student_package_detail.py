from extensions import db
from datetime import datetime, timezone
from enum import Enum


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


class Change(Enum):
    ADD = 1
    SUB = 2


# 消费类型 1：购买课时包 2：预约课程 3：无责取消预约 4：有责取消预约
class ChangeType(Enum):
    BUY = 1
    RESERVE = 2
    CANCEL_NO_RESPONSIBILITY = 3
    CANCEL_RESPONSIBILITY = 4


class StudentPackageDetail(db.Model):
    __tablename__ = 'student_package_details'

    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, nullable=False, default=0)
    student_package_id = db.Column(db.BigInteger, nullable=False, default=0)
    course_id = db.Column(db.BigInteger, nullable=False, default=0)
    title = db.Column(db.String(255), nullable=False, default='')
    hours = db.Column(db.Float, nullable=False, default=0)
    left_hours = db.Column(db.Float, nullable=False, default=0)
    change = db.Column(db.Integer, nullable=False, default=0)
    change_type = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<StudentPackageDetail %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_package_id': self.student_package_id,
            'course_id': self.course_id,
            'title': self.title,
            'hours': self.hours,
            'left_hours': self.left_hours,
            'change': self.change,
            'change_type': self.change_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
