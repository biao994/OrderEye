from datetime import datetime
from sqlalchemy import Table, inspect
from models import db, Order

class TimePartitionedOrder:
    _mapper = {}

    @staticmethod
    def model(timestamp):
        # 根据时间戳生成月份字符串，例如 "202304"
        month = datetime.fromtimestamp(timestamp).strftime("%Y%m")
        table_name = f'orders_{month}'

        if table_name not in TimePartitionedOrder._mapper:
            # 对每个 Column 对象进行复制，避免重复绑定
            columns = [c.copy() for c in Order.__table__.columns]
            new_table = Table(table_name, db.metadata, *columns, extend_existing=True)

            # 使用 inspect 检查表是否存在，不存在则创建
            if not inspect(db.engine).has_table(table_name):
                new_table.create(db.engine)

            # 动态创建模型类，绑定到新创建的表上
            Model = type('Order_' + month, (db.Model,), {'__table__': new_table})
            TimePartitionedOrder._mapper[table_name] = Model

        return TimePartitionedOrder._mapper[table_name]
