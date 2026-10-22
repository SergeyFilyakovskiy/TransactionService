from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.pdf.renderer import PdfReportRenderer
from app.infrastructure.postgres.repositories import (
    ReportFileRepository,
    ReportQueryRepository,
)
from app.infrastructure.postgres.session import async_session
from app.infrastructure.s3.report_storage import S3ReportStorage
from app.infrastructure.s3.s3_client import s3_client_cm


@dataclass
class WorkerContext:
    session: AsyncSession
    report_repo: ReportFileRepository
    query_repo: ReportQueryRepository
    renderer: PdfReportRenderer
    storage: S3ReportStorage


@asynccontextmanager
async def worker_context() -> AsyncGenerator[WorkerContext]:
    async with s3_client_cm() as s3_client:
        async with async_session() as session:
            try:
                yield WorkerContext(
                    session=session,
                    report_repo=ReportFileRepository(session),
                    query_repo=ReportQueryRepository(session),
                    renderer=PdfReportRenderer(),
                    storage=S3ReportStorage(
                        client=s3_client,
                        bucket=settings.minio_bucket,
                        public_endpoint=settings.minio_endpoint,
                    ),
                )
            except Exception:
                await session.rollback()
                raise
