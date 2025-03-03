# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:yourpassword@localhost/orders_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    
    # 钉钉告警配置：设置钉钉机器人 Webhook URL
    ALERT_CONFIG = {
        "dingtalk_webhook_url": os.environ.get("DINGTALK_WEBHOOK_URL", "https://oapi.dingtalk.com/robot/send?access_token=073b0fd30d527a39bdceaecba1b1d0f7c88058ed2c4fe934826f39db0d6fc602")
    }
