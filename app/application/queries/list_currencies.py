from dataclasses import dataclass

from app.domain.entities import Currency
from app.domain.interfaces import ICurrencyRepo


@dataclass(frozen=True)
class ListCurrenciesQuery:
    limit: int = 100
    offset: int = 0


class ListCurrenciesHandler:

    def __init__(self, currency_repo: ICurrencyRepo):
        self.currency_repo = currency_repo

    async def execute(self, query: ListCurrenciesQuery) -> list[Currency]:
        return await self.currency_repo.list(
            limit=query.limit,
            offset=query.offset,
        )
