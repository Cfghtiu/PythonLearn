import pika

# 建立到本地 RabbitMQ 服务器的连接
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# 创建一个通道
channel = connection.channel()

# 示例：声明一个队列
channel.queue_declare(queue='test_queue')

# 示例：向队列发送一条消息
channel.basic_publish(exchange='',
                      routing_key='test_queue',
                      body='Hello, RabbitMQ!',
                      )

print(" [x] Sent 'Hello, RabbitMQ!'")

# 关闭连接
connection.close()
