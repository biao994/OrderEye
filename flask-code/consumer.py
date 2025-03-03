# consumer.py
import json
import eventlet
from kafka import KafkaConsumer
from models import db
from anomaly import detect_anomaly
from alerts import send_custom_alert
from time_partition import TimePartitionedOrder  


def kafka_consumer(app, socketio):
    consumer = KafkaConsumer(
        'ecommerce_orders',
        bootstrap_servers='172.20.124.19:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id='web_dashboard',
        auto_offset_reset='latest'
    )
    with app.app_context():
        app.logger.info("Kafka 消费者已启动")
    for msg in consumer:
        order_data = msg.value
        socketio.emit('order_update', order_data)  # 实时推送到前端

        # 在应用上下文中处理异常检测、告警和数据库插入
        with app.app_context():
            # 异常检测
            is_anomaly, reason = detect_anomaly(order_data)
            order_data['is_anomaly'] = is_anomaly
            if is_anomaly:
                app.logger.info(f"异常订单检测：订单 {order_data['order_id']} 原因：{reason}")
                alert_config = app.config.get("ALERT_CONFIG", {})
                send_custom_alert(order_data, reason, alert_config)
            
            # 动态获取分区模型，根据订单 timestamp 来决定写入哪个子表
            PartitionModel = TimePartitionedOrder.model(order_data['timestamp'])
            
            # 避免重复插入：可根据订单号查找是否已存在于对应分区中
            exists = db.session.query(PartitionModel).filter_by(order_id=order_data['order_id']).first()
            if not exists:
                try:
                    new_order = PartitionModel(
                        order_id=order_data['order_id'],
                        user_id=order_data['user_id'],
                        event_type=order_data['event_type'],
                        amount=order_data['amount'],
                        province=order_data['province'],
                        city=order_data['city'],
                        timestamp=order_data['timestamp'],
                        is_anomaly=is_anomaly,
                        ip=order_data.get('ip'),
                        device_id=order_data.get('device_id')
                    )
                    db.session.add(new_order)
                    db.session.commit()
                    app.logger.info(f"订单 {order_data['order_id']} 已存入分区表 {PartitionModel.__tablename__}")
                except Exception as e:
                    app.logger.error(f"插入数据库失败: {e}")
                    db.session.rollback()
        eventlet.sleep(0)  # 让出协程
