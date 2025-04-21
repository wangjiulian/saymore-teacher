from extensions import db
from datetime import datetime, timezone


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


teacher_subjects = db.Table('teacher_subjects',
                            db.Column('teacher_id', db.BigInteger, db.ForeignKey('teachers.id'), primary_key=True),
                            db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True),
                            db.Column('created_at', db.Integer, default=get_utc_timestamp, nullable=False)
                            )


class TeacherSubject(db.Model):
    __tablename__ = 'teacher_subjects'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return f'<TeacherSubject {self.teacher_id}:{self.subject_id}>'
