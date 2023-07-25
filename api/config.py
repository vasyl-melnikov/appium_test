from pydantic import BaseSettings


class Settings(BaseSettings):
    rabbitmq_host: str
    rabbitmq_port: str
    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_virtual_host: str
    rabbitmq_queue_name: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: str
    postgres_host: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
