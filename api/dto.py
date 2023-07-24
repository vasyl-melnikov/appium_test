import datetime

from pydantic import BaseModel


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
