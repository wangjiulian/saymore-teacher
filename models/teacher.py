from extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash


def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())


# 定义教师-学科关联表
teacher_subjects = db.Table('teacher_subjects',
                            db.Column('teacher_id', db.BigInteger, db.ForeignKey('teachers.id'), primary_key=True),
                            db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True),
                            db.Column('created_at', db.Integer, default=get_utc_timestamp)
                            )


class Teacher(db.Model, UserMixin):
    __tablename__ = 'teachers'

    id = db.Column(db.BigInteger, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False, default='')
    gender = db.Column(db.Integer, default=0)  # 0: 未知, 1: 男, 2: 女
    avatar_url = db.Column(db.String(255))
    background = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    course_hours = db.Column(db.Float, default=0, nullable=False, comment='授课总课时')
    education_school = db.Column(db.String(100), nullable=False, default='')
    education_level = db.Column(db.Integer, default=0)  # 0: 未知, 1: 本科, 2: 硕士, 3: 博士
    teaching_start_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    teaching_experience = db.Column(db.Text)
    success_cases = db.Column(db.Text)
    teaching_achievements = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    is_recommend = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # 教师可教授的学科，使用teacher_subjects关联表
    subjects = db.relationship('Subject', secondary=teacher_subjects,
                               backref=db.backref('teachers', lazy='dynamic'),
                               lazy='dynamic')

    def get_id(self):
        # 用于Flask-Login用户标识
        return str(self.id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'nickname': self.nickname,
            'gender': self.gender,
            'avatar_url': self.avatar_url,
            'background': self.background,
            'video_url': self.video_url,
            'education_school': self.education_school,
            'education_level': self.education_level,
            'teaching_start_date': self.teaching_start_date.strftime('%Y-%m-%d') if self.teaching_start_date else None,
            'teaching_experience': self.teaching_experience,
            'success_cases': self.success_cases,
            'teaching_achievements': self.teaching_achievements,
            'notes': self.notes,
            'course_hours': self.course_hours,
            'is_active': self.is_active,
            'is_recommend': self.is_recommend,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f'<Teacher {self.name}>'
