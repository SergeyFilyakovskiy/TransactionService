from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.read_models import WeeklyReportRow


class IReportQueryRepo(ABC):

    @abstractmethod
    async def get_weekly_report(self, weeks: int = 52) -> list[WeeklyReportRow]: ...
