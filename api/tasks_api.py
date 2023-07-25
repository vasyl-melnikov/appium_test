import logging
from typing import Optional

import pika

from enum import Enum

from fastapi import APIRouter
from sqlmodel import Session, SQLModel

from config import settings
from database.db import engine
from database.models import Task
from dto import TaskModel, TaskDtoModel


class TaskStatus(Enum):
    CREATED = 'created'


router = APIRouter()
connection: Optional[pika.BlockingConnection] = None
channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)


@router.on_event("shutdown")
def on_shutdown():
    logger.debug("Closing connection with RabbitMQ")
    connection.close()


@router.on_event("startup")
def on_startup():
    global connection, channel

    logger.debug("Creating all necessary metadata for Postgres")
    SQLModel.metadata.create_all(engine)

    logger.debug("Creating connection to RabbitMQ")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host=settings.rabbitmq_virtual_host,
            credentials=pika.PlainCredentials(
                settings.rabbitmq_user, settings.rabbitmq_pass
            ),
            heartbeat=0
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue_name)


@router.post("/", response_model=Task)
def create_task(task: TaskDtoModel):
    with Session(engine) as session:
        new_task = Task(status=TaskStatus.CREATED.value)
        session.add(new_task)
        session.commit()
        new_task_id = new_task.id

    logger.info(f"Added new task {new_task_id} to database")

    channel.basic_publish(
        exchange="",
        routing_key=settings.rabbitmq_queue_name,
        body=TaskModel(task_id=new_task_id, **task.dict()).json().encode("utf-8"),
    )

    logger.info(f"Published task {new_task_id} to RabbitMQ for being completed")

    with Session(engine) as session:
        return session.get(Task, new_task_id)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    logger.info(f"Getting task {task_id} from database")
    with Session(engine) as session:
        return session.get(Task, task_id)


@router.get("/", response_model=list[Task])
def get_all_tasks():
    """
    This endpoint will return all tasks contained in database. But without results_body field.
    If you want to get results_body field, please use endpoint for getting exact task by id.
    """
    logger.info(f"Getting all tasks from database")

    with Session(engine) as session:
        data_list = list(session.execute(session.query(Task.id, Task.status)))
        task_list = [Task(id=id, status=status) for id, status in data_list]

    return task_list

