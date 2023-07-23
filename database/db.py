from sqlmodel import create_engine


db_url = "postgresql://my_user:my_password@localhost:5432/my_database"
engine = create_engine(db_url)


# if __name__ == "__main__":
#     # SQLModel.metadata.create_all(engine)
#     # create_task()
#     # read_task()