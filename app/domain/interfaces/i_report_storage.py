from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class IReportStorage(ABC):

    @abstractmethod
    async def upload_report(self, data: bytes, report_id: UUID) -> str: ...

    @abstractmethod
    async def delete_report(self, report_id: UUID) -> None: ...
