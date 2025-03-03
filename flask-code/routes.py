# routes.py
from flask import Blueprint, render_template, request, jsonify, current_app
from models import Order
from datetime import datetime
from utils import get_usd_to_cny_rate

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('dashboard.html')

@main_bp.route('/history')
def history():
    return render_template('history.html')

@main_bp.route('/orders', methods=['GET'])
def get_orders():
    try:
        limit = request.args.get('limit', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        currency = request.args.get('currency', 'CNY')
        anomaly_status = request.args.get('anomaly_status')
        usd_to_cny = get_usd_to_cny_rate() if currency.upper() == "USD" else 1
        
        # 解析查询日期范围，默认最近30天
        from datetime import datetime, timedelta
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_dt = datetime.now() - timedelta(days=30)
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end_dt = datetime.now()

        start_ts = int(start_dt.timestamp())
        # end_ts 取到当天结束（加一天）
        end_ts = int((end_dt + timedelta(days=1)).timestamp())

        # 生成从 start_dt 到 end_dt 涉及的月份列表
        months = []
        current = datetime(start_dt.year, start_dt.month, 1)
        while current <= end_dt:
            months.append(current.strftime("%Y%m"))
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)

        orders_combined = []
        # 遍历每个涉及的分区
        from time_partition import TimePartitionedOrder  # 动态分区模块
        for month in months:
            # 生成该月的代表性时间戳（本月第一天）
            ts = int(datetime.strptime(month, "%Y%m").timestamp())
            PartitionModel = TimePartitionedOrder.model(ts)
            # 对该分区进行查询，筛选时间范围
            query = PartitionModel.query.filter(
                PartitionModel.timestamp >= start_ts,
                PartitionModel.timestamp < end_ts
            )
            if anomaly_status == 'anomaly':
                query = query.filter(PartitionModel.is_anomaly == True)
            elif anomaly_status == 'normal':
                query = query.filter(PartitionModel.is_anomaly == False)
            orders = query.all()
            orders_combined.extend(orders)

        # 合并所有分区数据后，根据 timestamp 降序排序
        orders_combined.sort(key=lambda x: x.timestamp, reverse=True)
        orders_limited = orders_combined[:limit]

        result = []
        for order in orders_limited:
            converted_amount = order.amount / usd_to_cny
            result.append({
                "order_id": order.order_id,
                "user_id": order.user_id,
                "event_type": order.event_type,
                "amount": round(converted_amount, 2),
                "currency": "USD" if currency.upper() == "USD" else "CNY",
                "province": order.province,
                "city": order.city,
                "timestamp": order.timestamp,
                "date": datetime.fromtimestamp(order.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "is_anomaly": order.is_anomaly,
                "ip": order.ip,
                "device_id": order.device_id
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 新增接口：获取/更新钉钉告警设置
@main_bp.route('/alert-settings', methods=['GET', 'POST'])
def alert_settings():
    if request.method == 'POST':
        # 支持 JSON 或表单提交
        data = request.get_json() or request.form
        webhook_url = data.get('dingtalk_webhook_url')
        if not webhook_url:
            return jsonify({"error": "Webhook URL is required"}), 400
        current_app.config['ALERT_CONFIG']['dingtalk_webhook_url'] = webhook_url
        return jsonify({"message": "Alert settings updated", "alert_config": current_app.config['ALERT_CONFIG']})
    else:
        # 根据请求头判断是否返回 HTML 页面
        accept_header = request.headers.get("Accept", "")
        if "text/html" in accept_header:
            return render_template("alert_settings.html")
        else:
            return jsonify(current_app.config.get("ALERT_CONFIG"))
