from extensions import db
from datetime import datetime, timezone

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(32), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.Integer, default=get_utc_timestamp, onupdate=get_utc_timestamp, nullable=False)

    # 添加关系
    parent = db.relationship('Subject',
                             remote_side=[id],
                             backref=db.backref('children', lazy='dynamic'))

    def __repr__(self):
        return f'<Subject {self.name}>'

    def get_full_name(self):
        """获取完整的学科名称，如果有父级则返回 父级名称 - 当前名称，否则直接返回名称"""
        if self.parent_id and self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'full_name': self.get_full_name()
        }

    @staticmethod
    def get_all_subjects():
        """获取所有科目"""
        subjects = Subject.query.order_by(Subject.id).all()
        return subjects
