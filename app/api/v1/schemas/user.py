from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .base import EntityModel


class UserResponse(EntityModel):
    id: UUID
    email: str
    is_frozen: bool
    created_at: datetime
    updated_at: datetime


class FreezeUserRequest(BaseModel):
    user_id: UUID


class UnfreezeUserRequest(BaseModel):
    user_id: UUID
