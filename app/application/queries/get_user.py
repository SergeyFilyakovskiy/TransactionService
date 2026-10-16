from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import User
from app.domain.exceptions import UserNotFoundError
from app.domain.interfaces import IUserRepo


@dataclass(frozen=True)
class GetUserQuery:
    user_id: UUID


class GetUserHandler:
    def __init__(self, user_repo: IUserRepo):
        self.user_repo = user_repo

    async def execute(self, query: GetUserQuery) -> User:
        user = await self.user_repo.get_by_id(query.user_id)

        if user is None:
            raise UserNotFoundError()

        return user
