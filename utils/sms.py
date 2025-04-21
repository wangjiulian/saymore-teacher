import json
import random
import requests
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)


class AliSmsClient:
    """
    阿里云短信服务客户端
    """
    def __init__(self, access_key_id=None, access_key_secret=None):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.api_url = "https://dysmsapi.aliyuncs.com"
        
    def send_verification_code(self, phone, code, template_code=None, sign_name=None):
        """
        发送验证码
        
        :param phone: 手机号
        :param code: 验证码
        :param template_code: 短信模板代码
        :param sign_name: 短信签名
        :return: (success, message)
        """
        if not self.access_key_id or not self.access_key_secret:
            logger.warning("未配置阿里云短信服务凭证，无法发送短信")
            return False, "短信服务未配置"
        
        # 如果未传入，则使用配置中的默认值
        template_code = template_code or current_app.config.get('SMS_TEMPLATE_CODE')
        sign_name = sign_name or current_app.config.get('SMS_SIGN_NAME')
        
        if not template_code or not sign_name:
            logger.warning("短信模板或签名未配置")
            return False, "短信服务配置不完整"
            
        try:
            # 组装请求参数
            params = {
                "PhoneNumbers": phone,
                "SignName": sign_name,
                "TemplateCode": template_code,
                "TemplateParam": json.dumps({"code": code})
            }
            
            # 调用阿里云短信API
            # 注意：这里只做示例，实际调用阿里云API需要进行签名等处理
            # 在实际项目中，建议使用阿里云官方SDK
            
            # 这里是模拟调用，实际项目中替换为真实的API调用代码
            logger.info(f"模拟发送短信到 {phone}，验证码: {code}")
            
            # 实际项目中，取消下面注释并实现真实的API调用
            # response = requests.post(self.api_url, data=params)
            # result = response.json()
            # if result.get("Code") == "OK":
            #     return True, "发送成功"
            # return False, result.get("Message", "未知错误")
            
            # 测试环境中，假设总是发送成功
            return True, "发送成功"
            
        except Exception as e:
            logger.error(f"发送短信失败: {str(e)}")
            return False, f"发送失败: {str(e)}"


def send_verification_sms(phone, code):
    """
    发送验证码短信
    
    :param phone: 手机号
    :param code: 验证码
    :return: (success, message)
    """
    # 获取配置的阿里云短信服务凭证
    access_key_id = current_app.config.get('SMS_ACCESS_KEY_ID')
    access_key_secret = current_app.config.get('SMS_ACCESS_KEY_SECRET')
    
    # 创建短信客户端
    sms_client = AliSmsClient(access_key_id, access_key_secret)
    
    # 发送短信
    success, message = sms_client.send_verification_code(phone, code)
    
    # 记录发送结果
    logger.info(f"短信发送结果: 手机号={phone}, 验证码={code}, 成功={success}, 消息={message}")
    
    return success, message 