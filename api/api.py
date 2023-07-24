import datetime

import pika

from fastapi import FastAPI
from sqlmodel import Session, select
from pydantic import BaseModel

from database.db import engine
from database.models import Task
from config import settings

app = FastAPI()

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        virtual_host=settings.rabbitmq_virtual_host,
        credentials=pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_pass)
    )
)
channel = connection.channel()
channel.queue_declare(queue=settings.rabbitmq_queue_name)


class DateModel(BaseModel):
    start_date: datetime.datetime
    end_date: datetime.datetime


class TaskDtoModel(BaseModel):
    hotel_name: str
    dates: list[DateModel]


class TaskModel(BaseModel):
    task_id: int
    hotel_name: str
    dates: list[DateModel]


@app.on_event('shutdown')
def on_shutdown():
    connection.close()


@app.post('/tasks')
def create_task(task: TaskDtoModel):
    with Session(engine) as session:
        new_task = Task(status='created')
        session.add(new_task)
        session.commit()
        new_task_id = new_task.id
    channel.basic_publish(
        exchange='',
        routing_key=settings.rabbitmq_queue_name,
        body=TaskModel(task_id=new_task_id, **task.dict()).json().encode('utf-8')
    )


@app.get('/tasks/{task_id}', response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        return session.get(Task, task_id)


@app.get('/tasks', response_model=list[Task])
def get_all_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
