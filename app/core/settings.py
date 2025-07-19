from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    MINIO_HOST: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BEARER_TOKEN: str

    BUCKET_TO_PROCESS: str
    BUCKET_PROCESSED: str

    RABBITMQ_HOST: str


settings = Settings()  # type: ignore
