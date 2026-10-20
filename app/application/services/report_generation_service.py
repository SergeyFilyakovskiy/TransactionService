from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ReportFile
from app.domain.exceptions import ReportFileNotFoundError
from app.domain.interfaces import (
    IPdfRenderer,
    IReportFileRepo,
    IReportQueryRepo,
    IReportStorage,
)

logger = logging.getLogger(__name__)


class ReportGenerationService:

    def __init__(
        self,
        session: AsyncSession,
        report_repo: IReportFileRepo,
        query_repo: IReportQueryRepo,
        renderer: IPdfRenderer,
        storage: IReportStorage,
    ) -> None:
        self.session = session
        self.report_repo = report_repo
        self.query_repo = query_repo
        self.renderer = renderer
        self.storage = storage

    async def generate(self, report_id: UUID) -> ReportFile:
        report = await self.report_repo.get_by_id(report_id)

        if report is None:
            raise ReportFileNotFoundError()

        report.mark_processing()
        await self.report_repo.save(report)
        await self.session.commit()

        try:
            rows = await self.query_repo.get_weekly_report(weeks=52)

            pdf_bytes = self.renderer.render_weekly_report(
                rows=rows,
                generated_at=datetime.now(timezone.utc),
            )

            url = await self.storage.upload_report(pdf_bytes, report.id)

            report.mark_completed(url=url)
            await self.report_repo.save(report)
            await self.session.commit()

        except Exception:
            logger.exception("Report generation failed: %s", report_id)

            await self.session.rollback()

            report.mark_failed()
            await self.report_repo.save(report)
            await self.session.commit()

            raise

        return report
