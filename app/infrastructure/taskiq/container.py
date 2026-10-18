from __future__ import annotations

from contextlib import aclosing
from dataclasses import dataclass
from typing import Any, AsyncIterator

import aioboto3
from botocore.config import Config

from app.core.config import settings
from app.core.dependencies import get_pdf_renderer, get_postgres_session
from app.infrastructure.postgres.repositories import (
    ReportFileRepository,
    ReportQueryRepository,
)
from app.infrastructure.s3.report_storage import S3ReportStorage


@dataclass
class WorkerContext:
    session: Any
    report_repo: ReportFileRepository
    query_repo: ReportQueryRepository
    renderer: Any
    storage: S3ReportStorage
    s3_client: Any


async def worker_context() -> AsyncIterator[WorkerContext]:
    boto_session = aioboto3.Session()

    s3_cm = boto_session.client(
        "s3",
        endpoint_url=settings.minio_endpoint,
        aws_access_key_id=settings.minio_access_key.get_secret_value(),
        aws_secret_access_key=settings.minio_secret_key.get_secret_value(),
        region_name=settings.minio_region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )

    async with s3_cm as s3_client:
        async with aclosing(get_postgres_session()) as session_gen:
            session = await session_gen.__anext__()

            yield WorkerContext(
                session=session,
                report_repo=ReportFileRepository(session),
                query_repo=ReportQueryRepository(session),
                renderer=await get_pdf_renderer(),
                storage=S3ReportStorage(
                    client=s3_client,
                    bucket=settings.minio_bucket,
                    public_endpoint=settings.minio_endpoint,
                ),
                s3_client=s3_client,
            )
