from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Currency
from app.domain.interfaces.i_currency_repo import ICurrencyRepo
from app.domain.value_objects import CurrencyCode
from app.infrastructure.postgres.models import CurrencyORM


class CurrencyRepository(ICurrencyRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, currency: Currency) -> None:
        orm = await self.session.get(CurrencyORM, currency.id)

        if orm is None:
            orm = self._to_orm(currency)
            self.session.add(orm)
        else:
            orm.code = currency.code.value
            orm.name = currency.name
            orm.updated_at = currency.updated_at

    async def get_by_id(self, currency_id: UUID) -> Currency | None:
        orm = await self.session.get(CurrencyORM, currency_id)
        return self._to_entity(orm) if orm else None

    async def get_by_code(self, code: str) -> Currency | None:
        normalized_code = CurrencyCode(code).value

        orm = await self.session.scalar(
            select(CurrencyORM).where(CurrencyORM.code == normalized_code)
        )

        return self._to_entity(orm) if orm else None

    async def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Currency]:
        result = await self.session.scalars(
            select(CurrencyORM).order_by(CurrencyORM.code).limit(limit).offset(offset)
        )

        return [self._to_entity(orm) for orm in result.all()]

    async def delete(self, currency_id: UUID) -> None:
        orm = await self.session.get(CurrencyORM, currency_id)

        if orm:
            await self.session.delete(orm)

    async def exists_by_code(self, code: str) -> bool:
        normalized_code = CurrencyCode(code).value

        result = await self.session.scalar(
            select(exists().where(CurrencyORM.code == normalized_code))
        )

        return bool(result)

    def _to_entity(self, orm: CurrencyORM) -> Currency:
        return Currency(
            id=orm.id,
            code=CurrencyCode(orm.code),
            name=orm.name,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _to_orm(self, currency: Currency) -> CurrencyORM:
        return CurrencyORM(
            id=currency.id,
            code=currency.code.value,
            name=currency.name,
            created_at=currency.created_at,
            updated_at=currency.updated_at,
        )
