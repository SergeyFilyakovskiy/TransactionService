from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import ReportStatus
from app.domain.entities import ReportFile
from app.domain.interfaces.i_report_repo import IReportFileRepo
from app.infrastructure.postgres.models import ReportFilesORM


class ReportFileRepository(IReportFileRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, report: ReportFile) -> None:
        orm = await self.session.get(ReportFilesORM, report.id)

        if orm is None:
            orm = self._to_orm(report)
            self.session.add(orm)
        else:
            orm.status = report.status.value
            orm.url = report.url
            orm.updated_at = report.updated_at

    async def get_by_id(self, report_id: UUID) -> ReportFile | None:
        orm = await self.session.get(ReportFilesORM, report_id)
        return self._to_entity(orm) if orm else None

    async def get_by_url(self, url: str) -> ReportFile | None:
        orm = await self.session.scalar(
            select(ReportFilesORM).where(ReportFilesORM.url == url)
        )

        return self._to_entity(orm) if orm else None

    async def list_by_user(
        self,
        user_id: UUID,
        *,
        status: ReportStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ReportFile]:
        stmt = select(ReportFilesORM).where(ReportFilesORM.user_id == user_id)

        if status is not None:
            stmt = stmt.where(ReportFilesORM.status == status.value)

        stmt = (
            stmt.order_by(ReportFilesORM.created_at.desc()).limit(limit).offset(offset)
        )

        result = await self.session.scalars(stmt)

        return [self._to_entity(orm) for orm in result.all()]

    async def delete(self, report_id: UUID) -> None:
        orm = await self.session.get(ReportFilesORM, report_id)

        if orm:
            await self.session.delete(orm)

    def _to_entity(self, orm: ReportFilesORM) -> ReportFile:
        return ReportFile(
            id=orm.id,
            user_id=orm.user_id,
            status=(
                orm.status
                if isinstance(orm.status, ReportStatus)
                else ReportStatus(orm.status)
            ),
            url=orm.url,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _to_orm(self, report: ReportFile) -> ReportFilesORM:
        return ReportFilesORM(
            id=report.id,
            user_id=report.user_id,
            status=report.status.value,
            url=report.url,
            created_at=report.created_at,
            updated_at=report.updated_at,
        )
