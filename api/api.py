import datetime

import pika

from fastapi import FastAPI
from sqlmodel import Session, select
from pydantic import BaseModel

from database.db import engine
from database.models import Task

app = FastAPI()

rabbitmq_host = 'localhost'
rabbitmq_port = 5672
rabbitmq_user = 'guest'
rabbitmq_pass = 'guest'
rabbitmq_virtual_host = '/'
rabbitmq_queue_name = 'my_tasks_queue'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host=rabbitmq_virtual_host,
        credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    )
)
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue_name)


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
        routing_key=rabbitmq_queue_name,
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
