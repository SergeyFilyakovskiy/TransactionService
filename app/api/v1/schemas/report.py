from datetime import datetime
from uuid import UUID

from app.core.enums import ReportStatus

from .base import EntityModel


class ReportResponse(EntityModel):
    id: UUID
    user_id: UUID
    status: ReportStatus
    url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
