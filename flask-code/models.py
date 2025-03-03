# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.String(50))
    event_type = db.Column(db.String(50))
    amount = db.Column(db.Float)
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    timestamp = db.Column(db.BigInteger)
    is_anomaly = db.Column(db.Boolean, default=False)
    ip = db.Column(db.String(50))
    device_id = db.Column(db.String(50))
