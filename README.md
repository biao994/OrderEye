OrderEye 订单之眼

OrderEye 是一个基于 Go + Kafka + Flask 构建的 实时订单数据处理与监控系统，支持 订单数据模拟生成、Kafka 消息传输、异常检测、实时告警与可视化展示，并结合 PostgreSQL 进行高效存储和查询。

✨ 项目特色

✅ 高并发订单数据实时生成

利用 Go 语言并发机制，采用多个 worker 协程同时生成订单数据，实现高吞吐量数据模拟。

可通过命令行参数灵活设置发送数量、并发数及发送延时，满足不同性能需求。

✅ Kafka 异步消息队列

订单数据通过 Kafka 进行异步分发，提升系统扩展性和高并发处理能力。

✅ 实时监控与可视化

Flask + SocketIO 实现 Web 端实时数据流监控，订单数据自动刷新。

订单历史可查询，异常订单高亮显示。

✅ 异常检测与告警

采用规则检测，对同一个ip的设备下单频率进行实时分析。

异常订单触发钉钉告警。

✅ 汇率爬取 & 订单金额转换

通过爬取最新汇率信息，实现订单金额的实时转换与展示。

✅ 高效存储优化

采用 PostgreSQL 分表策略，按每月存储订单数据，提升查询效率，支持高并发访问。


🖥 功能截图

📌 订单实时监控

![image](https://github.com/user-attachments/assets/27feda94-4378-436c-8686-7823f87220c7)

📌 异常订单高亮展示

![image](https://github.com/user-attachments/assets/cda93ae3-e785-47d7-bd7c-2faf006e7baa)

📌 钉钉告警配置

![image](https://github.com/user-attachments/assets/07ad2127-c3d4-440d-baca-76fdcf10c21d)

📌 钉钉消息截图

<img width="472" alt="image" src="https://github.com/user-attachments/assets/2f839a05-08ab-4aeb-8f44-e6cb6cc83555" />

📌 数据库分表截图

<img width="484" alt="image" src="https://github.com/user-attachments/assets/c248b643-28cd-4a99-8ceb-a18f762228ef" />



