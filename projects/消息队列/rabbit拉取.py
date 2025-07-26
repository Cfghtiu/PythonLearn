import pika


# 回调函数，当收到消息时自动触发
def callback(ch, method, properties, body):
    print(f"收到消息: {body} {properties}")

    # 手动确认消息已处理（如果 auto_ack=False）
    ch.basic_ack(delivery_tag=method.delivery_tag)


# 建立连接
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# 声明队列（确保队列存在）
channel.queue_declare(queue='test_queue')

# 订阅队列，设置回调函数
channel.basic_consume(
    queue='test_queue',
    on_message_callback=callback,
    auto_ack=False  # 设置为 False 可以手动确认消息
)
# 手动拉取
# channel.basic_get(queue='test_queue', auto_ack=False)

print('等待消息中... (Ctrl+C 退出)')

# 开始监听队列
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("消费者已停止")
    connection.close()
