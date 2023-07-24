from fastapi import FastAPI

from api import tasks

app = FastAPI()
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
