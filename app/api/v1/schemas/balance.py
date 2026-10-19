from datetime import datetime
from decimal import Decimal
from uuid import UUID

from .base import EntityModel


class BalanceResponse(EntityModel):
    id: UUID
    user_id: UUID
    currency_id: UUID
    amount: Decimal
    created_at: datetime
    updated_at: datetime
