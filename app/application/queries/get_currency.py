from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Currency
from app.domain.exceptions import CurrencyNotFoundError
from app.domain.interfaces import ICurrencyRepo


@dataclass(frozen=True)
class GetCurrencyQuery:
    currency_id: UUID


class GetCurrencyHandler:

    def __init__(self, currency_repo: ICurrencyRepo):
        self.currency_repo = currency_repo

    async def execute(self, query: GetCurrencyQuery) -> Currency:
        currency = await self.currency_repo.get_by_id(query.currency_id)

        if currency is None:
            raise CurrencyNotFoundError()

        return currency
