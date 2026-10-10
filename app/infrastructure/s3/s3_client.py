from contextlib import asynccontextmanager

import aioboto3
from botocore.config import Config
from fastapi import FastAPI, Request

from app.core.config import settings


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
        aws_access_key_id=settings.minio_access_key.get_secret_value(),
        aws_secret_access_key=settings.minio_secret_key.get_secret_value(),
        region_name=settings.minio_region,
        config=boto_config,
    )

    app.state.s3_client = await client_cm.__aenter__()

    yield

    await client_cm.__aexit__(None, None, None)


async def get_s3_client(request: Request):
    return request.app.state.s3_client
