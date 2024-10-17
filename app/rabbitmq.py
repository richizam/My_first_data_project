# app/rabbitmq.py

import pika
import os
import json

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
QUEUE_NAME = "resume_tasks"

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials('guest', 'guest')  # Используйте правильные креденшелы
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
    return connection

def publish_resume_task(resume_data):
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    message = json.dumps(resume_data)
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сделать сообщение устойчивым
        )
    )
    connection.close()