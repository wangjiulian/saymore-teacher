from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, comment='Phone Number')
    avatar_url = db.Column(db.String(255), comment='Avatar')
    nickname = db.Column(db.String(50), nullable=False, comment='Nickname')
    gender = db.Column(db.Integer, default=0, comment='Gender: 1-Male, 2-Female, 0-Unspecified')
    birth_date = db.Column(db.Date, comment='Birth Date')
    student_type = db.Column(db.Integer, default=0,
                             comment='Student Type: 1-Preschooler, 2-Elementary Student, 3-Middle School Student, 4-High School Student, 5-College Student, 6-Professional')
    learning_purpose = db.Column(db.Integer,
                                 comment='Learning Purpose: 1-IELTS, 2-TOEFL, 3-General English Proficiency, 4-Business English, 5-Conversational')
    english_level = db.Column(db.Integer, default=0,
                              comment='English Level: 1-Never Learned English, 2-Can Say Simple Words, 3-Can Speak Complete Sentences, 4-Can Communicate Fluently, 5-Excellent')
    is_active = db.Column(db.Boolean, default=True, comment='Account Status: 1-Active, 0-Disabled')
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'nickname': self.nickname,
            'gender': self.gender,
            'birth_date': self.birth_date.strftime('%Y-%m-%d') if self.birth_date else None,
            'student_type': self.student_type,
            'learning_purpose': self.learning_purpose,
            'english_level': self.english_level,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def get_gender_text(gender):
        gender_map = {0: 'Unspecified', 1: 'Male', 2: 'Female'}
        return gender_map.get(gender, 'Unknown')

    @staticmethod
    def get_student_type_text(student_type):
        student_type_map = {
            1: 'Preschooler',
            2: 'Elementary Student',
            3: 'Middle School Student',
            4: 'High School Student',
            5: 'College Student',
            6: 'Professional'
        }
        return student_type_map.get(student_type, 'Unknown')

    @staticmethod
    def get_english_level_text(english_level):
        level_map = {
            1: 'Never Learned English',
            2: 'Can Say Simple Words',
            3: 'Can Speak Complete Sentences',
            4: 'Can Communicate Fluently',
            5: 'Excellent'
        }
        return level_map.get(english_level, 'Unknown')

    def get_learning_purpose_text(self):
        purpose_map = {
            1: 'IELTS',
            2: 'TOEFL',
            3: 'General English Proficiency',
            4: 'Business English',
            5: 'Conversational'
        }

        if self.learning_purpose:
            return purpose_map.get(self.learning_purpose, 'Unknown')
        else:
            return 'Not Set'
