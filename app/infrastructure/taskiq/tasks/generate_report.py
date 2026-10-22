from __future__ import annotations

import logging
from uuid import UUID

from app.application.services.report_generation_service import ReportGenerationService
from app.core.config import settings
from app.infrastructure.taskiq.broker import broker
from app.infrastructure.taskiq.container import worker_context

logger = logging.getLogger(__name__)


@broker.task(
    task_name="reports.generate_weekly",
    max_retries=settings.taskiq_max_retries,
)
async def generate_report_task(report_id: str) -> None:
    logger.info("Report generation started: %s", report_id)

    async with worker_context() as ctx:
        service = ReportGenerationService(
            session=ctx.session,
            report_repo=ctx.report_repo,
            query_repo=ctx.query_repo,
            renderer=ctx.renderer,
            storage=ctx.storage,
        )

        await service.generate(UUID(report_id))

    logger.info("Report generation finished: %s", report_id)
