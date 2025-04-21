from extensions import db
from datetime import datetime, timezone

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class StudentPackage(db.Model):
    __tablename__ = 'student_packages'
    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, nullable=False, default=0)
    name = db.Column(db.String(255), nullable=False, default='')
    subject_id = db.Column(db.Integer, nullable=False, default=0)
    hours = db.Column(db.Float, nullable=False, default=0)
    left_hours = db.Column(db.Float, nullable=False, default=0)
    description = db.Column(db.String(255), nullable=False, default='')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<StudentPackage %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'subject_id': self.subject_id,
            'hours': self.hours,
            'left_hours': self.left_hours,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
