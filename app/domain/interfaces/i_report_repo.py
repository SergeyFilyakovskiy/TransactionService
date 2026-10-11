from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.core.enums import ReportStatus
from app.domain.entities import ReportFile


class IReportFileRepo(ABC):

    @abstractmethod
    async def save(self, report: ReportFile) -> None:
        """Create or update report file."""
        ...

    @abstractmethod
    async def get_by_id(self, report_id: UUID) -> ReportFile | None: ...

    @abstractmethod
    async def get_by_url(self, url: str) -> ReportFile | None: ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: UUID,
        *,
        status: ReportStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ReportFile]: ...

    @abstractmethod
    async def delete(self, report_id: UUID) -> None: ...
