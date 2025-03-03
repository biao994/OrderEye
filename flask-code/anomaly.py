# anomaly.py
from models import Order,db
from time_partition import TimePartitionedOrder

def detect_anomaly(order_data):
    order_timestamp = int(order_data["timestamp"])
    ip = order_data["ip"]
    device_id = order_data["device_id"]
    
    # 计算时间范围（当前时间戳及前5分钟）
    start_time = order_timestamp - 300
    end_time = order_timestamp
    
    # 获取所有涉及的分区表模型（可能跨月）
    partitions = set()
    for ts in [start_time, end_time]:
        partition_model = TimePartitionedOrder.model(ts)
        partitions.add(partition_model)
    
    # 遍历所有分区表统计总数
    total_count = 0
    for model in partitions:
        count = db.session.query(model).filter(
            model.ip == ip,
            model.device_id == device_id,
            model.timestamp >= start_time,
            model.timestamp <= end_time
        ).count()
        total_count += count
    
    if total_count >= 10:
        return True, f"同一IP+设备5分钟内下单{total_count}次"
    return False, "正常"

