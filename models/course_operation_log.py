from extensions import db
from datetime import datetime, timezone
from enum import Enum
from models.admin_user import AdminUser
from models.student import Student
from models.teacher import Teacher

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class OperatorType(Enum):
    TEACHER = 1
    STUDENT = 2
    ADMIN = 3

class CourseOperationLog(db.Model):
    __tablename__ = 'course_operation_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True, comment='Log ID')
    course_id = db.Column(db.BigInteger, nullable=False, index=True, comment='Associated Course ID')
    operator_id = db.Column(db.BigInteger, nullable=False, index=True, comment='Operator ID')
    operator_type = db.Column(db.Integer, nullable=False, comment='Operator Type')
    old_status = db.Column(db.Integer, nullable=False, comment='Original Status')
    new_status = db.Column(db.Integer, nullable=False, comment='New Status')
    operation_time = db.Column(db.Integer, default=get_utc_timestamp, nullable=False, comment='Operation Timestamp')
    cancel_reason = db.Column(db.String(255), nullable=False, default='', comment='Cancellation Reason')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def __repr__(self):
        return f'<CourseOperationLog {self.id}>'

    def get_status_text(self, status_code):
        """Get status text"""
        status_map = {
            0: "Not Set",
            1: "Pending Class",
            2: "In Progress",
            3: "Completed",
            4: "Cancelled"
        }
        return status_map.get(status_code, "Unknown Status")

    def get_operator_type_text(self):
        """Get operator type text"""
        type_map = {
            1: "Admin Teacher",
            2: "Teacher",
            3: "Student"
        }
        return type_map.get(self.operator_type, "Unknown Type")

    def get_operation_text(self):
        """Get operation description text"""
        if self.old_status == 1 and self.new_status == 2:
            return "Start Class"
        elif self.old_status == 2 and self.new_status == 3:
            return "End Class"
        elif self.new_status == 4:
            return "Cancel Class"
        else:
            return f"{self.get_status_text(self.new_status)}"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'operator_id': self.operator_id,
            'operator_type': self.operator_type,
            'operator_type_text': self.get_operator_type_text(),
            'old_status': self.old_status,
            'new_status': self.new_status,
            'old_status_text': self.get_status_text(self.old_status),
            'new_status_text': self.get_status_text(self.new_status),
            'operation_text': self.get_operation_text(),
            'operation_time': self.operation_time,
            'cancel_reason': self.cancel_reason,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'operator_name': self.get_operator_name()
        }

    def get_operator_name(self):
        # Implementation of get_operator_name method
        pass
