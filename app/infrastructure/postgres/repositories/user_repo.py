from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.domain.interfaces.i_user_repo import IUserRepo
from app.domain.value_objects import Email, HashedPassword
from app.infrastructure.postgres.models import UserORM


class UserRepository(IUserRepo):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── User CRUD ─────────────────────────────────────────

    async def save(self, user: User) -> None:
        orm = await self.session.get(UserORM, user.id)

        if orm is None:
            # Create new user
            orm = self._user_to_orm(user)
            self.session.add(orm)

        else:
            orm.email = user.email.value
            orm.hashed_password = user.hashed_password.value

    async def get_by_id(self, user_id: UUID) -> User | None:
        orm = await self.session.scalar(select(UserORM).where(UserORM.id == user_id))
        return self._to_entity(orm) if orm else None

    async def get_by_email(self, email: str) -> User | None:
        orm = await self.session.scalar(
            select(UserORM).where(UserORM.email == email.lower())
        )

        return self._to_entity(orm) if orm else None

    async def delete(self, user_id: UUID) -> None:
        orm = await self.session.get(UserORM, user_id)
        if orm:
            await self.session.delete(orm)

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.scalar(
            select(exists().where(UserORM.email == email.lower()))
        )
        return bool(result)

    def _to_entity(self, orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=Email(orm.email),
            hashed_password=(HashedPassword.from_hash(orm.hashed_password)),
            is_frozen=orm.is_frozen,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    # ── Mapping Entity → ORM ──────────────────────────────

    def _user_to_orm(self, user: User) -> UserORM:
        return UserORM(
            id=user.id,
            email=user.email.value,
            hashed_password=(
                user.hashed_password.value if user.hashed_password else None
            ),
            is_frozen=user.is_frozen,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
