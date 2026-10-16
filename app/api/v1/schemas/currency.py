from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .base import EntityModel


class CurrencyCreateRequest(BaseModel):
    code: str = Field(..., min_length=2, max_length=10, pattern=r"^[A-Z0-9]+$")
    name: str = Field(..., min_length=1, max_length=100)


class CurrencyUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CurrencyResponse(EntityModel):
    id: UUID
    code: str
    name: str
    created_at: datetime
    updated_at: datetime
