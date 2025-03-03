package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"math/rand"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"time"

	"github.com/IBM/sarama"
	"github.com/bxcodec/faker/v3"
)

// 电商订单事件结构
type OrderEvent struct {
	OrderID   string  `json:"order_id"`
	UserID    string  `json:"user_id"`
	EventType string  `json:"event_type"`
	Amount    float64 `json:"amount"`
	Province  string  `json:"province"`
	City      string  `json:"city"`
	Timestamp int64   `json:"timestamp"`
	IP        string  `json:"ip"`
	DeviceID  string  `json:"device_id"`
}

// 省份城市数据池（可扩展）
var provinceCityPool = map[string][]string{
	"广东": {"深圳", "广州", "东莞"},
	"浙江": {"杭州", "宁波", "温州"},
	"江苏": {"南京", "苏州", "无锡"},
}

func main() {
	// 命令行参数：最大消息数、并发生产者数量、消息间延时（毫秒）
	var maxMessages int64
	var numWorkers int
	var delayMs int
	flag.Int64Var(&maxMessages, "max", 100000, "最大发送消息数量")
	flag.IntVar(&numWorkers, "workers", 10, "并发生产者数量")
	flag.IntVar(&delayMs, "delay", 100, "每条消息发送延时（毫秒）")
	flag.Parse()

	// Kafka 生产者配置
	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForAll      // 等待所有副本确认
	config.Producer.Retry.Max = 3                         // 最大重试次数
	config.Producer.Return.Successes = true               // 启用成功回调
	config.Producer.Compression = sarama.CompressionSnappy // 启用压缩

	producer, err := sarama.NewAsyncProducer([]string{"localhost:9092"}, config)
	if err != nil {
		log.Fatalf("生产者创建失败: %v", err)
	}
	defer producer.Close()

	// 信号处理
	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	// 启动监控协程，监控消息发送状态
	go monitorDeliveries(producer)

	// 用于记录已生成的消息数量（原子计数）
	var producedCount int64 = 0

	// 等待组，用于等待所有生产者协程结束
	var wg sync.WaitGroup
	wg.Add(numWorkers)

	// done 通道用于提前终止所有协程
	done := make(chan struct{})

	// 启动一个 goroutine 监控信号
	go func() {
		<-signals
		fmt.Println("\n收到终止信号，正在关闭...")
		close(done)
	}()

	// 启动 worker 协程
	for i := 0; i < numWorkers; i++ {
		go func(workerId int) {
			defer wg.Done()
			for {
				// 检查是否收到退出信号
				select {
				case <-done:
					return
				default:
				}

				// 原子增加计数，判断是否达到最大消息数
				current := atomic.AddInt64(&producedCount, 1)
				if current > maxMessages {
					return
				}

				// 生成订单事件并序列化
				event := generateOrderEvent()
				message, err := json.Marshal(event)
				if err != nil {
					log.Printf("序列化失败: %v", err)
					continue
				}

				// 发送消息到 Kafka
				producer.Input() <- &sarama.ProducerMessage{
					Topic: "ecommerce_orders",
					Value: sarama.ByteEncoder(message),
				}

				// 延时控制
				time.Sleep(time.Duration(delayMs) * time.Millisecond)
			}
		}(i)
	}

	// 等待所有 worker 结束
	wg.Wait()
	fmt.Printf("总共发送消息数量: %d\n", producedCount)
}

// 生成电商订单事件
func generateOrderEvent() OrderEvent {
	province := randomProvince()
	city := randomCity(province)
	amount := rand.Float64()*450 + 50 // 正常订单金额

	ip := randomNormalIP()           // 随机正常 IP
	deviceID := randomNormalDevice() // 随机设备 ID

	return OrderEvent{
		OrderID:   faker.UUIDDigit(),
		UserID:    faker.Username(),
		EventType: randomEventType(),
		Amount:    amount,
		Province:  province,
		City:      city,
		Timestamp: time.Now().Unix(),
		IP:        ip,
		DeviceID:  deviceID,
	}
}

// 监控消息发送状态
func monitorDeliveries(p sarama.AsyncProducer) {
	for {
		select {
		case success, ok := <-p.Successes():
			if !ok {
				return
			}
			log.Printf("✅ 发送成功 | Topic=%s | Partition=%d | Offset=%d\n",
				success.Topic, success.Partition, success.Offset)
		case err, ok := <-p.Errors():
			if !ok {
				return
			}
			log.Printf("❌ 发送失败 | Error=%v\n", err.Err)
		}
	}
}

// 随机事件类型生成
func randomEventType() string {
	types := []string{"order_create", "order_pay", "order_deliver"}
	return types[rand.Intn(len(types))]
}

// 随机省份生成
func randomProvince() string {
	provinces := make([]string, 0, len(provinceCityPool))
	for k := range provinceCityPool {
		provinces = append(provinces, k)
	}
	return provinces[rand.Intn(len(provinces))]
}

// 随机城市生成
func randomCity(province string) string {
	cities := provinceCityPool[province]
	return cities[rand.Intn(len(cities))]
}

// 随机生成正常 IP 地址
func randomNormalIP() string {
	// 模拟部分 IP 更频繁出现
	ips := []string{
		"192.168.1.101", "192.168.1.101", "192.168.1.101", // 高频 IP
		"192.168.1.102", "192.168.1.103",
		"219.76.10.25", "223.5.5.5",
	}
	return ips[rand.Intn(len(ips))]
}

// 随机生成正常设备ID
func randomNormalDevice() string {
	// 模拟部分设备ID更频繁出现
	devices := []string{
		"device_A", "device_A", "device_A", // 高频设备
		"device_B", "device_C",
	}
	return devices[rand.Intn(len(devices))]
}
