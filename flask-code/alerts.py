# alerts.py
import requests
import logging


def send_dingtalk_alert(subject, message, webhook_url):
    """
    通过钉钉机器人 Webhook 发送告警消息，使用文本消息类型
    """
    try:
        payload = {
            "msgtype": "text",
            "text": {
                "content": f"{subject}\n{message}"
            },
            "at": {
                "atMobiles": [],
                "isAtAll": False  # 可设为 True 全部通知
            }
        }
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code != 200:
            logging.error(f"钉钉告警发送失败: {response.status_code} - {response.text}")
        else:
            logging.info("钉钉告警发送成功。")
    except Exception as e:
        logging.error(f"钉钉告警异常: {e}")

def send_custom_alert(order, reason, alert_config):
    """
    根据告警配置，通过钉钉发送异常订单告警
    order: 异常订单数据字典
    reason: 异常原因
    alert_config: 告警配置字典，必须包含钉钉 webhook URL
    """
    subject = f"异常订单告警：{order.get('order_id')}"
    message = f"订单 {order.get('order_id')} 异常，原因：{reason}\n"
    
    webhook_url = alert_config.get("dingtalk_webhook_url")
    if webhook_url:
        send_dingtalk_alert(subject, message, webhook_url)
    else:
        logging.error("未配置钉钉告警的 webhook_url")
