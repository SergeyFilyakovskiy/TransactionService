# s3_client.py
from contextlib import asynccontextmanager

import aioboto3
from botocore.config import Config
from fastapi import Depends, FastAPI, Request

from app.core.config import settings

# Глобальная переменная для хранения клиента, но мы будем обращаться к ней только через app.state
# Это стандартный паттерн FastAPI для ресурсов с жизненным циклом.


@asynccontextmanager
async def lifespan(app: FastAPI):

    session = aioboto3.Session()

    boto_config = Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        max_pool_connections=settings.minio_max_pool_connections,
    )

    client_cm = session.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        region_name=settings.minio_region,
        config=boto_config,
    )

    app.state.s3_client = await client_cm.__aenter__()

    yield

    await client_cm.__aexit__(None, None, None)


async def get_s3_client(request: Request):

    return request.app.state.s3_client
