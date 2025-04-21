from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, SubmitField, DateTimeField, IntegerField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime, timedelta
from flask import current_app

class AvailabilitySearchForm(FlaskForm):
    """
    可预约时间搜索表单
    """
    start_date = DateField('开始日期', format='%Y-%m-%d', validators=[])
    end_date = DateField('结束日期', format='%Y-%m-%d', validators=[])
    submit = SubmitField('搜索')
    
    def validate_end_date(self, field):
        """确保结束日期大于等于开始日期"""
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError('结束日期必须大于等于开始日期')

class AvailabilityBatchForm(FlaskForm):
    """
    批量添加可预约时间表单
    """
    date = DateField('选择日期', format='%Y-%m-%d', validators=[
        DataRequired(message='请选择日期')
    ])
    
    start_time = TimeField('开始时间', format='%H:%M', validators=[
        DataRequired(message='请选择开始时间')
    ])
    
    end_time = TimeField('结束时间', format='%H:%M', validators=[
        DataRequired(message='请选择结束时间')
    ])
    
    submit = SubmitField('添加可预约时间')
    
    def validate_date(self, field):
        """确保日期不小于今天"""
        today = datetime.now().date()
        if field.data < today:
            raise ValidationError('日期不能早于今天')
    
    def validate_start_time(self, field):
        """确保开始时间不小于当前时间（如果日期是今天）"""
        if self.date.data and field.data:
            # 如果选择的是今天
            today = datetime.now().date()
            if self.date.data == today:
                now = datetime.now().time()
                if field.data <= now:
                    raise ValidationError('如果选择今天，开始时间必须大于当前时间')
    
    def validate_end_time(self, field):
        """确保结束时间大于开始时间"""
        if self.start_time.data and field.data and field.data <= self.start_time.data:
            raise ValidationError('结束时间必须大于开始时间')
            
    def get_datetime_ranges(self):
        """
        根据表单数据计算出时间范围列表
        返回: [(start_timestamp, end_timestamp), ...]
        """
        from constants import CLASS_DURATION_MINUTES
        
        ranges = []
        if not (self.date.data and self.start_time.data and self.end_time.data):
            return ranges
            
        # 合并日期和时间
        start_dt = datetime.combine(self.date.data, self.start_time.data)
        end_dt = datetime.combine(self.date.data, self.end_time.data)
        
        # 如果结束时间小于或等于开始时间，认为是跨天的情况
        if end_dt <= start_dt:
            end_dt = end_dt + timedelta(days=1)
            
        # 记录调试信息
        current_app.logger.info(f"生成时间段 - 日期: {self.date.data}, 开始: {self.start_time.data}, 结束: {self.end_time.data}")
        current_app.logger.info(f"计算后 - 开始时间: {start_dt}, 结束时间: {end_dt}")
            
        # 按照CLASS_DURATION_MINUTES分钟划分时间段
        current = start_dt
        while current + timedelta(minutes=CLASS_DURATION_MINUTES) <= end_dt:
            next_slot = current + timedelta(minutes=CLASS_DURATION_MINUTES)
            ranges.append((
                int(current.timestamp()),
                int(next_slot.timestamp())
            ))
            current = next_slot
            
        current_app.logger.info(f"生成了 {len(ranges)} 个时间段")
        return ranges 