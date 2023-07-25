import pika

from enum import Enum

from fastapi import APIRouter
from sqlmodel import Session, select, SQLModel

from config import settings
from database.db import engine
from database.models import Task
from dto import TaskModel, TaskDtoModel


class TaskStatus(Enum):
    CREATED = 'created'


router = APIRouter()

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


@router.on_event("shutdown")
def on_shutdown():
    connection.close()


@router.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@router.post("/")
def create_task(task: TaskDtoModel):
    with Session(engine) as session:
        new_task = Task(status=TaskStatus.CREATED.value)
        session.add(new_task)
        session.commit()
        new_task_id = new_task.id

    channel.basic_publish(
        exchange="",
        routing_key=settings.rabbitmq_queue_name,
        body=TaskModel(task_id=new_task_id, **task.dict()).json().encode("utf-8"),
    )


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        return session.get(Task, task_id)


@router.get("/", response_model=list[Task])
def get_all_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()
