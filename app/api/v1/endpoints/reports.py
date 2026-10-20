from uuid import UUID

from fastapi import APIRouter
from starlette import status

from app.api.v1.schemas.report import ReportResponse
from app.application.commands.generate_report import GenerateReportCommand
from app.core.dependencies import (
    AccessTokenDep,
    GenerateReportHandlerDep,
    TokenServiceDep,
)
from app.infrastructure.taskiq.tasks import generate_report_task

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_report(
    access_token: AccessTokenDep,
    handler: GenerateReportHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    report = await handler.execute(GenerateReportCommand(user_id=user_id))
    await generate_report_task.kiq(str(report.id))

    return report
