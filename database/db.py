from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, select, Session


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str
    result_body: str


sqlite_url = "postgresql://testuser:testuser@localhost:5432/testdb"

engine = create_engine(sqlite_url, echo=True)
def create_task():
    with Session(engine) as session:
        new_task = Task(status='done', result_body='here we are')
        session.add(new_task)
        session.commit()
def read_task():
    with Session(engine) as session:
        statement = select(Task)
        results = session.exec(statement)
        print(results)
if __name__ == "__main__":
    # SQLModel.metadata.create_all(engine)
    # create_task()
    read_task()