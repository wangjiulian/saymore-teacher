from extensions import db
from datetime import datetime, timezone

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class TeacherCompensationCourse(db.Model):
    __tablename__ = 'teacher_compensation_courses'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='主键 ID')
    teacher_id = db.Column(db.BigInteger, nullable=False, default=0, index=True, comment='老师 ID')
    student_id = db.Column(db.BigInteger, nullable=False, default=0, index=True, comment='学生 ID')
    total_hours = db.Column(db.Float, nullable=False, default=0, comment='累计补偿课时')
    left_hours = db.Column(db.Float, nullable=False, default=0, comment='剩余补偿课时')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<TeacherCompensationCourse %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'total_hours': self.total_hours,
            'left_hours': self.left_hours,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
