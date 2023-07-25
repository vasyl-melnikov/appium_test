from fastapi import FastAPI

import tasks_api

from config import settings

app = FastAPI()
app.include_router(tasks_api.router, prefix="/tasks", tags=["tasks"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host)
