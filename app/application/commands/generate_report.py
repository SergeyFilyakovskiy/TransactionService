from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ReportFile
from app.domain.exceptions import UserNotFoundError
from app.domain.interfaces import IReportFileRepo, IUserRepo


@dataclass(frozen=True)
class GenerateReportCommand:
    user_id: UUID


class GenerateReportHandler:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
        report_repo: IReportFileRepo,
    ):
        self.session = session
        self.user_repo = user_repo
        self.report_repo = report_repo

    async def execute(self, command: GenerateReportCommand) -> ReportFile:
        user = await self.user_repo.get_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError()

        report = ReportFile.create(user_id=command.user_id)

        await self.report_repo.save(report)
        await self.session.commit()

        # report.mark_processing()
        # await self.report_repo.save(report)
        # await self.session.commit()

        return report
