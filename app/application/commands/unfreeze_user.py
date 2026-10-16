from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.exceptions import UserNotFoundError
from app.domain.interfaces import IUserRepo


@dataclass(frozen=True)
class UnfreezeUserCommand:
    user_id: UUID


class UnfreezeUserHandler:

    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
    ):
        self.session = session
        self.user_repo = user_repo

    async def execute(self, command: UnfreezeUserCommand) -> User:
        user = await self.user_repo.get_by_id(command.user_id)

        if user is None:
            raise UserNotFoundError()

        user.unfreeze()

        await self.user_repo.save(user)
        await self.session.commit()

        return user
