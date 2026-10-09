from __future__ import annotations

import time
from dataclasses import dataclass
from uuid import UUID

from app.application.services.token_service import TokenService
from app.domain.exceptions import InvalidTokenError
from app.domain.interfaces.i_token_store import ITokenStore


@dataclass
class LogoutUserCommand:
    access_token: str
    user_id: UUID


class LogoutUserHandler:

    def __init__(
        self,
        token_store: ITokenStore,
        token_service: TokenService,
    ) -> None:
        self.token_store = token_store
        self.token_service = token_service

    async def handle(self, command: LogoutUserCommand) -> None:

        # 1. Decode access token for jti и exp
        payload = self.token_service.decode_token(command.access_token)

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Token missing JTI")

        # 2. Calculating remaining access token live time for TTL blacklist

        remaining_ttl = int(payload["exp"] - time.time())

        if remaining_ttl > 0:
            # Add in blacklist only if token isn't expired
            await self.token_store.blacklist_token(jti, ttl=remaining_ttl)

        # 3. Delete refresh token
        await self.token_store.delete_refresh_token(command.user_id)
