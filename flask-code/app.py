# app.py
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
from config import Config
from models import db
from routes import main_bp
from consumer import kafka_consumer

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库和 SocketIO
db.init_app(app)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# 注册蓝图
app.register_blueprint(main_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # 启动 Kafka 消费者线程
    eventlet.spawn(kafka_consumer, app, socketio)
    # 启动 Flask 服务
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
