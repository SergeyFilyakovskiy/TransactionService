from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import ReportFile
from app.domain.exceptions import ReportFileNotFoundError
from app.domain.interfaces import IReportFileRepo


@dataclass(frozen=True)
class GetReportQuery:
    report_id: UUID


class GetReportHandler:

    def __init__(self, report_repo: IReportFileRepo):
        self.report_repo = report_repo

    async def execute(self, query: GetReportQuery) -> ReportFile:
        report = await self.report_repo.get_by_id(query.report_id)

        if report is None:
            raise ReportFileNotFoundError()

        return report
