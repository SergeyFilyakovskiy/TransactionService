from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands.login_user import LoginUserHandler
from app.application.commands.logout_user import LogoutUserHandler
from app.application.commands.refresh_token import RefreshTokenHandler
from app.application.commands.register_user import RegisterUserHandler
from app.application.queries.verify_token import VerifyTokenHandler
from app.application.services.token_service import TokenService
from app.infrastructure.postgres.repositories.user_repo import UserRepository
from app.infrastructure.postgres.session import async_session
from app.infrastructure.redis.token_store import RedisTokenStore

bearer_scheme = HTTPBearer(auto_error=False)


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.aclose()


async def get_redis(request: Request):
    return request.app.state.redis


async def get_user_repo(
    session: AsyncSession = Depends(get_postgres_session),
) -> UserRepository:
    return UserRepository(session)


async def get_token_store(redis=Depends(get_redis)) -> RedisTokenStore:
    return RedisTokenStore(redis)


def get_token_service() -> TokenService:
    return TokenService()


def get_register_handler(
    user_repo=Depends(get_user_repo),
) -> RegisterUserHandler:
    return RegisterUserHandler(user_repo)


def get_login_handler(
    user_repo=Depends(get_user_repo),
    token_store=Depends(get_token_store),
    token_service=Depends(get_token_service),
) -> LoginUserHandler:
    return LoginUserHandler(user_repo, token_store, token_service)


def get_refresh_handler(
    user_repo=Depends(get_user_repo),
    token_store=Depends(get_token_store),
    token_service=Depends(get_token_service),
) -> RefreshTokenHandler:
    return RefreshTokenHandler(user_repo, token_store, token_service)


def get_logout_handler(
    token_store=Depends(get_token_store),
    token_service=Depends(get_token_service),
) -> LogoutUserHandler:
    return LogoutUserHandler(token_store, token_service)


def get_verify_handler(
    token_store=Depends(get_token_store),
    token_service=Depends(get_token_service),
) -> VerifyTokenHandler:
    return VerifyTokenHandler(token_store, token_service)


async def get_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    return credentials.credentials
