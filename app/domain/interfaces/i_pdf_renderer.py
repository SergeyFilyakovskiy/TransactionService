from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.read_models import WeeklyReportRow


class IPdfRenderer(ABC):

    @abstractmethod
    def render_weekly_report(
        self,
        rows: list[WeeklyReportRow],
        generated_at: datetime,
    ) -> bytes: ...
