import json
import datetime

import pika

from enum import Enum

from sqlmodel import Session
from appium import webdriver

from parser import TrapAdvisorParser
from database.models import Task
from database.db import engine
from config import settings


class TaskStatus(Enum):
    DONE = 'done'
    PENDING = 'pending'


caps = {
    "appium:automationName": settings.appium_automation_name,
    "platformName": settings.appium_platform_name,
    "appium:ensureWebviewsHavePages": settings.appium_ensure_webviews_have_pages,
    "appium:nativeWebScreenshot": settings.appium_native_web_screenshot,
    "appium:newCommandTimeout": settings.appium_new_command_timeout,
    "appium:connectHardwareKeyboard": settings.appium_connect_hardware_keyboard,
}

driver = webdriver.Remote(f"http://{settings.appium_host}:{settings.appium_port}", caps)
trap_advisor_parser = TrapAdvisorParser(driver)
date_format = "%Y-%m-%d"


def process_task(ch, method, properties, body):
    body_dict = json.loads(body.decode())

    with Session(engine) as session:
        found_task = session.get(Task, body_dict["task_id"])
        found_task.status = TaskStatus.PENDING.value
        session.add(found_task)
        session.commit()

    all_parsed_data = {body_dict["hotel_name"]: []}

    for date in body_dict["dates"]:
        parsed_data = trap_advisor_parser.parse_data(
            prompt=body_dict["hotel_name"],
            start_date=datetime.datetime.strptime(date["start_date"][:10], date_format),
            end_date=datetime.datetime.strptime(date["end_date"][:10], date_format),
        )
        all_parsed_data[body_dict["hotel_name"]].append(parsed_data)

    with Session(engine) as session:
        found_task = session.get(Task, body_dict["task_id"])
        found_task.result_body = str(all_parsed_data)
        found_task.status = TaskStatus.DONE.value
        session.add(found_task)
        session.commit()

    ch.basic_ack(delivery_tag=method.delivery_tag)


# Create a connection to RabbitMQ server
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        virtual_host=settings.rabbitmq_virtual_host,
        credentials=pika.PlainCredentials(
            settings.rabbitmq_user, settings.rabbitmq_pass
        ),
    )
)
channel = connection.channel()
channel.queue_declare(queue=settings.rabbitmq_queue_name)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(
    queue=settings.rabbitmq_queue_name, on_message_callback=process_task
)

print("Waiting for tasks. To exit, press CTRL+C")
channel.start_consuming()
