from __future__ import annotations

from dataclasses import dataclass

from app.application.dto import TokenPairDTO
from app.application.services.token_service import TokenService
from app.domain.exceptions import InvalidCredentialsError, TooManyAttemptsError
from app.domain.interfaces.i_token_store import ITokenStore
from app.domain.interfaces.i_user_repo import IUserRepo

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_TTL = 300


@dataclass
class LoginUserCommand:
    email: str
    password: str


class LoginUserHandler:

    def __init__(
        self,
        user_repo: IUserRepo,
        token_store: ITokenStore,
        token_service: TokenService,
    ) -> None:
        self.user_repo = user_repo
        self.token_store = token_store
        self.token_service = token_service

    async def handle(self, command: LoginUserCommand) -> TokenPairDTO:

        attempts = await self.token_store.get_failed_attempts(command.email)
        if attempts >= MAX_FAILED_ATTEMPTS:
            raise TooManyAttemptsError()

        user = await self.user_repo.get_by_email(command.email)

        if not user or not user.verify_password(command.password):
            await self.token_store.increment_failed_attempts(
                command.email,
                ttl=LOCKOUT_TTL,
            )
            raise InvalidCredentialsError()

        await self.token_store.reset_failed_attempts(command.email)

        return await self.token_service.create_token_pair(user, self.token_store)
