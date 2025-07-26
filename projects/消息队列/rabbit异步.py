import asyncio
import pika
from pika.adapters.asyncio_connection import AsyncioConnection


class AsyncRabbitMQConsumer:
    def __init__(self, host='localhost', queue_name='test_queue'):
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    async def on_message(self, ch, method, properties, body):
        print(f"收到消息: {body}")
        # 手动确认消息
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def on_open(self, connection):
        """连接建立后的回调"""
        self.connection = connection
        self.connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """通道建立后的回调"""
        self.channel = channel
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.on_message
        )
        print("开始监听队列...")

    async def connect(self):
        loop = asyncio.get_event_loop()
        self.connection = AsyncioConnection(
            pika.ConnectionParameters(host=self.host),
            on_open_callback=self.on_open,
            custom_ioloop=loop
        )

    async def run(self):
        await self.connect()
        await asyncio.Future()  # 保持运行直到手动中断


# 启动异步消费者
if __name__ == '__main__':
    asyncio.run(AsyncRabbitMQConsumer().run())
