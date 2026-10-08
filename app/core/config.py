from pathlib import Path

from pydantic import Field
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Config(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        case_sensitive=True,
        extra="ignore",
    )

    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: SecretStr = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(validation_alias="POSTGRES_PORT")
    postgres_db_name: str = Field(validation_alias="POSTGRES_DB")

    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_region: str = "us-east-1"
    minio_bucket: str = "files"
    minio_max_pool_connections: int = 50

    jwt_secret: SecretStr = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(validation_alias="JWT_ALGORITHM")
    jwt_access_expire: int = Field(validation_alias="JWT_ACCESS_EXPIRE")
    jwt_refresh_expire: int = Field(validation_alias="JWT_REFRESH_EXPIRE")

    redis_password: SecretStr = Field(validation_alias="REDIS_PASSWORD")
    redis_host: str = Field(validation_alias="REDIS_HOST")
    redis_port: str = Field(validation_alias="REDIS_PORT")
    redis_db: str = Field(validation_alias="REDIS_AUTH_DB")

    @property
    def db_async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}"
        )

    @property
    def db_migrations_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db_name}"
        )

    @property
    def redis_url(self) -> str:
        return (
            f"redis://:{self.redis_password.get_secret_value()}"
            f"@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        )


settings = Config()  # pyright: ignore[reportCallIssue]
