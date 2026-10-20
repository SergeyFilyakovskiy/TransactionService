from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import TransactionStatus, TransactionType

from .base import EntityModel


class DepositRequest(BaseModel):
    currency_id: UUID
    amount: float = Field(..., gt=0, decimal_places=8)


class WithdrawRequest(BaseModel):
    currency_id: UUID
    amount: float = Field(..., gt=0, decimal_places=8)


class CancelTransactionRequest(BaseModel):
    transaction_id: UUID


class TransactionResponse(EntityModel):
    id: UUID
    user_id: UUID
    currency_id: UUID
    amount: float
    type: TransactionType
    status: TransactionStatus
    cancelled_transaction_id: UUID | None
    created_at: datetime
    updated_at: datetime
