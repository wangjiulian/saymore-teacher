from extensions import db
from datetime import datetime, timezone

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class StudentTrialQuota(db.Model):
    __tablename__ = 'student_trial_quotas'
    id = db.Column(db.BigInteger, primary_key=True)
    student_id = db.Column(db.BigInteger, nullable=False, default=0)
    course_id = db.Column(db.BigInteger, nullable=False, default=0)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return '<StudentTrialQuota %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
