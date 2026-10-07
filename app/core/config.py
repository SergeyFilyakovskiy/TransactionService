# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_region: str = "us-east-1"
    minio_bucket: str = "files"
    minio_max_pool_connections: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
