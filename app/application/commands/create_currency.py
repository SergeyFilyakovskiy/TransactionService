from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Currency
from app.domain.exceptions import CurrencyAlreadyExistsError
from app.domain.interfaces import ICurrencyRepo


@dataclass(frozen=True)
class CreateCurrencyCommand:
    code: str
    name: str


class CreateCurrencyHandler:

    def __init__(
        self,
        session: AsyncSession,
        currency_repo: ICurrencyRepo,
    ):
        self.session = session
        self.currency_repo = currency_repo

    async def execute(self, command: CreateCurrencyCommand) -> Currency:
        if await self.currency_repo.exists_by_code(command.code):
            raise CurrencyAlreadyExistsError(command.code)

        currency = Currency.create(
            code=command.code,
            name=command.name,
        )

        await self.currency_repo.save(currency)
        await self.session.commit()

        return currency
