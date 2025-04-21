from extensions import db
from datetime import datetime, timedelta, timezone
import time


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


class TeacherAvailability(db.Model):
    __tablename__ = 'teacher_availabilities'

    id = db.Column(db.BigInteger, primary_key=True)
    teacher_id = db.Column(db.BigInteger, nullable=False, default=0, index=True)
    course_id = db.Column(db.BigInteger, nullable=False, default=0)  # 关联的课程ID，0表示未被预约
    start_time = db.Column(db.Integer, nullable=False, default=0)  # Keep as timestamp
    end_time = db.Column(db.Integer, nullable=False, default=0)  # Keep as timestamp
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # 关联到Teacher模型
    teacher = db.relationship('Teacher',
                              primaryjoin="TeacherAvailability.teacher_id == Teacher.id",
                              foreign_keys=[teacher_id],
                              backref=db.backref('availabilities', lazy='dynamic'))

    # 关联到Course模型（如果course_id > 0）
    course = db.relationship('Course',
                             primaryjoin="TeacherAvailability.course_id == Course.id",
                             foreign_keys=[course_id],
                             backref=db.backref('availability', uselist=False),
                             uselist=False)

    def __repr__(self):
        return f'<TeacherAvailability {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'course_id': self.course_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'created_at': self.created_at,  # Keep as timestamp
            'updated_at': self.updated_at  # Keep as timestamp
        }

    def get_start_datetime(self):
        """返回开始时间的datetime对象"""
        return datetime.fromtimestamp(self.start_time)

    def get_end_datetime(self):
        """返回结束时间的datetime对象"""
        return datetime.fromtimestamp(self.end_time)

    def get_date_str(self):
        """返回日期字符串（年月日）"""
        return self.get_start_datetime().strftime('%Y-%m-%d')

    def get_start_time_str(self):
        """返回开始时间字符串（时分）"""
        return self.get_start_datetime().strftime('%H:%M')

    def get_end_time_str(self):
        """返回结束时间字符串（时分）"""
        return self.get_end_datetime().strftime('%H:%M')

    def is_booked(self):
        """检查该时间段是否已被预约"""
        return self.course_id > 0

    def is_expired(self):
        """检查该时间段是否已过期（开始时间小于当前时间）"""
        current_time = int(datetime.now().timestamp())
        return self.start_time < current_time

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
