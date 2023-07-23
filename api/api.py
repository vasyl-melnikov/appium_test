from fastapi import FastAPI

app = FastAPI()

@app.post('/tasks/create_task')
def create_task():
    pass

@app.get('/task_status/{task_id}')
def get_task(task_id: str):
    pass

@app.get('/tasks')
def get_task(task_id: str):
    pass