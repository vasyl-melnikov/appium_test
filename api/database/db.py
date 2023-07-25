from sqlmodel import create_engine

from config import settings

db_url = (
    f"postgresql://{settings.postgres_user}:"
    f"{settings.postgres_password}@"
    f"{settings.postgres_host}:"
    f"{settings.postgres_port}/"
    f"{settings.postgres_db}"
)
engine = create_engine(db_url)


# if __name__ == "__main__":
#     # SQLModel.metadata.create_all(engine)
#     # create_task()
#     # read_task()
