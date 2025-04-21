from extensions import db
from datetime import datetime, timedelta, timezone
import random
import time

def get_utc_timestamp():
    """Returns the current UTC timestamp as an integer."""
    return int(datetime.now(timezone.utc).timestamp())

class SmsVerification(db.Model):
    __tablename__ = 'sms_verifications'
    
    id = db.Column(db.BigInteger, primary_key=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Integer, default=get_utc_timestamp, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 添加过期时间（非数据库字段）
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, phone, code=None, expiry_seconds=300):
        self.phone = phone
        # 如果没有传入验证码，则随机生成6位数字验证码
        self.code = code if code else ''.join(random.choice('0123456789') for _ in range(6))
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds)
    
    @classmethod
    def generate_code(cls, phone, expiry_seconds=300, test_mode=False):
        """
        为指定手机号生成验证码
        
        :param phone: 手机号
        :param expiry_seconds: 过期时间（秒）
        :param test_mode: 测试模式，如果为True则返回固定的"1233"作为验证码
        :return: SmsVerification对象
        """
        # 在测试模式下，生成固定的"1233"作为验证码
        code = "1233" if test_mode else None
        verification = cls(phone=phone, code=code, expiry_seconds=expiry_seconds)
        db.session.add(verification)
        db.session.commit()
        return verification
    
    @classmethod
    def verify_code(cls, phone, code):
        """
        验证手机号和验证码是否匹配
        
        :param phone: 手机号
        :param code: 验证码
        :return: 如果验证成功返回True，否则返回False
        """
        # 查找最近一条未使用的验证码记录
        verification = cls.query.filter_by(
            phone=phone,
            code=code,
            is_used=False
        ).order_by(cls.created_at.desc()).first()
        
        if verification:
            # 计算距离创建时间过去了多少秒
            elapsed = datetime.now(timezone.utc) - verification.created_at
            # 如果未超过5分钟（300秒），则验证成功
            if elapsed.total_seconds() < 300:
                # 标记为已使用
                verification.is_used = True
                db.session.commit()
                return True
        
        return False
    
    @classmethod
    def can_send_new_code(cls, phone, limit_seconds=60):
        """
        检查是否可以向指定手机号发送新的验证码
        
        :param phone: 手机号
        :param limit_seconds: 限制时间（秒）
        :return: 如果可以发送返回True，否则返回False
        """
        # 查找最近一条发送记录
        last_verification = cls.query.filter_by(
            phone=phone
        ).order_by(cls.created_at.desc()).first()
        
        if not last_verification:
            return True
        
        # 检查最后一次发送是否超过限制时间
        time_since_last = datetime.now(timezone.utc) - last_verification.created_at
        return time_since_last.total_seconds() > limit_seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'code': self.code,
            'is_used': self.is_used,
            'created_at': self.created_at,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SmsVerification {self.phone}>' 