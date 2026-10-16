from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.exceptions import UserNotFoundError
from app.domain.interfaces import IUserRepo


@dataclass(frozen=True)
class FreezeUserCommand:
    user_id: UUID


class FreezeUserHandler:

    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
    ):
        self.session = session
        self.user_repo = user_repo

    async def execute(self, command: FreezeUserCommand) -> User:
        user = await self.user_repo.get_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError()

        user.freeze()

        await self.user_repo.save(user)
        await self.session.commit()

        return user
