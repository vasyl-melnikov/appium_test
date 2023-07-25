from pydantic import BaseSettings


class Settings(BaseSettings):
    rabbitmq_host: str
    rabbitmq_port: str
    rabbitmq_user: str
    rabbitmq_pass: str
    rabbitmq_virtual_host: str
    rabbitmq_queue_name: str
    appium_host: str
    appium_port: str
    appium_automation_name: str
    appium_platform_name: str
    appium_native_web_screenshot: bool = True
    appium_ensure_webviews_have_pages: bool = True
    appium_new_command_timeout: int = 3600
    appium_connect_hardware_keyboard: bool = True
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: str
    postgres_host: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
