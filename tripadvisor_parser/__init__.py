import datetime

import pika
import json

from sqlmodel import Session
from appium import webdriver

from parser import TrapAdvisorParser
from database.models import Task
from database.db import engine


# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_pass = 'guest'
rabbitmq_virtual_host = '/'
rabbitmq_queue_name = 'my_tasks_queue'

caps = {
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    "appium:ensureWebviewsHavePages": True,
    "appium:nativeWebScreenshot": True,
    "appium:newCommandTimeout": 3600,
    "appium:connectHardwareKeyboard": True,
}

driver = webdriver.Remote("http://localhost:4723", caps)
trap_advisor_parser = TrapAdvisorParser(driver)
date_format = '%Y-%m-%d'

def process_task(ch, method, properties, body):
    body_dict = json.loads(body.decode())
    with Session(engine) as session:
        found_task = session.get(Task, body_dict['task_id'])
        found_task.status = 'in_progress'
        session.add(found_task)
        session.commit()
    all_parsed_data = {body_dict['hotel_name']: []}
    for date in body_dict['dates']:
        parsed_data = trap_advisor_parser.parse_data(prompt=body_dict['hotel_name'],
                                                     start_date=datetime.datetime.strptime(date['start_date'][:10], date_format),
                                                     end_date=datetime.datetime.strptime(date['end_date'][:10], date_format))
        all_parsed_data[body_dict['hotel_name']].append(parsed_data)
    with Session(engine) as session:
        found_task = session.get(Task, body_dict['task_id'])
        found_task.result_body = str(all_parsed_data)
        found_task.status = 'done'
        session.add(found_task)
        session.commit()

    ch.basic_ack(delivery_tag=method.delivery_tag)


# Create a connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_virtual_host,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    )
)

# Create a channel
channel = connection.channel()

# Declare a queue (in case it does not exist)
channel.queue_declare(queue=rabbitmq_queue_name)

# Set the prefetch count to 1 (allowing only one unacknowledged message at a time)
channel.basic_qos(prefetch_count=1)

# Set up a consumer to receive messages from the queue
channel.basic_consume(queue=rabbitmq_queue_name, on_message_callback=process_task)

# Start consuming messages
print("Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()
