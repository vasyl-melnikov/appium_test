from fastapi import FastAPI
from sqlmodel import Session, select
from database.db import engine
from database.models import Task

app = FastAPI()


@app.post('/tasks/')
def create_task():
    pass


@app.get('/tasks/{task_id}', response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        return session.get(Task, task_id)


@app.get('/tasks/', response_model=list[Task])
def get_all_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)