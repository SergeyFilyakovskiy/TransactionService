from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions import CurrencyNotFoundError
from app.domain.interfaces import ICurrencyRepo


@dataclass(frozen=True)
class DeleteCurrencyCommand:
    currency_id: UUID


class DeleteCurrencyHandler:

    def __init__(
        self,
        session: AsyncSession,
        currency_repo: ICurrencyRepo,
    ):
        self.session = session
        self.currency_repo = currency_repo

    async def execute(self, command: DeleteCurrencyCommand) -> None:
        currency = await self.currency_repo.get_by_id(command.currency_id)

        if currency is None:
            raise CurrencyNotFoundError()

        await self.currency_repo.delete(command.currency_id)
        await self.session.commit()
