from typing import Annotated, Callable
from fastapi import Depends
import pika

from app.core.settings import settings

from abc import ABC


class Queue(ABC):
    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(settings.RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def close(self):
        self.connection.close()


class SendQueue(Queue):
    def add_to_queue(self, message: str):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )


class ReceiveQueue(Queue):
    def receive_message(self, on_message: Callable[[str], None]):
        self.on_message = on_message

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback
        )
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        self.on_message(body.decode("utf-8"))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def close(self):
        self.channel.stop_consuming()
        self.connection.close()
