from __future__ import annotations

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, AsyncGenerator, cast

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, Request

from app.core.config import settings


def _boto_config() -> Config:
    return Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        max_pool_connections=settings.minio_max_pool_connections,
    )


@asynccontextmanager
async def s3_client_cm() -> AsyncGenerator[Any]:

    session = aioboto3.Session()

    client_cm = cast(
        AbstractAsyncContextManager[Any],
        session.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key.get_secret_value(),
            aws_secret_access_key=settings.minio_secret_key.get_secret_value(),
            region_name=settings.minio_region,
            config=_boto_config(),
        ),
    )

    async with client_cm as client:
        yield client


@asynccontextmanager
async def s3_lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with s3_client_cm() as client:
        app.state.s3_client = client

        try:
            await client.head_bucket(Bucket=settings.minio_bucket)
        except ClientError:
            await client.create_bucket(Bucket=settings.minio_bucket)

        yield


async def get_s3_client(request: Request):
    return request.app.state.s3_client
