from extensions import db
from datetime import datetime, timezone
from enum import Enum

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class TeacherCompensationCourseLogType(Enum):
    COMPENSATION = 1
    USE_COMPENSATION = 2

class TeacherCompensationCourseLog(db.Model):
    __tablename__ = 'teacher_compensation_course_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键 ID')
    teacher_id = db.Column(db.BigInteger, nullable=False, default=0, index=True, comment='老师 ID')
    student_id = db.Column(db.BigInteger, nullable=False, default=0, index=True, comment='学生 ID')
    course_id = db.Column(db.BigInteger, nullable=False, default=0, index=True, comment='课程 ID')
    hours = db.Column(db.Float, nullable=False, default=0, comment='补偿课时数量')
    type = db.Column(db.Integer, nullable=False, default=1, comment='操作类型：1-需补偿（如取消） 2-使用补偿')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<TeacherCompensationCourseLog %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'hours': self.hours,
            'type': self.type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
