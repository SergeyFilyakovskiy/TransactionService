from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Currency
from app.domain.exceptions import CurrencyNotFoundError
from app.domain.interfaces import ICurrencyRepo


@dataclass(frozen=True)
class UpdateCurrencyCommand:
    currency_id: UUID
    name: str


class UpdateCurrencyHandler:

    def __init__(
        self,
        session: AsyncSession,
        currency_repo: ICurrencyRepo,
    ):
        self.session = session
        self.currency_repo = currency_repo

    async def execute(self, command: UpdateCurrencyCommand) -> Currency:
        currency = await self.currency_repo.get_by_id(command.currency_id)

        if currency is None:
            raise CurrencyNotFoundError()

        currency.change_name(command.name)

        await self.currency_repo.save(currency)
        await self.session.commit()

        return currency
