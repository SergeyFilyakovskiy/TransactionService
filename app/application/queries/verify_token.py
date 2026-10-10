from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.application.services.token_service import TokenService
from app.domain.exceptions import InvalidTokenError
from app.domain.interfaces.i_token_store import ITokenStore


@dataclass
class VerifyTokenQuery:
    access_token: str


@dataclass
class VerifiedUserDTO:
    user_id: UUID
    email: str
    role: str


class VerifyTokenHandler:

    def __init__(
        self,
        token_store: ITokenStore,
        token_service: TokenService,
    ) -> None:
        self.token_store = token_store
        self.token_service = token_service

    async def handle(self, query: VerifyTokenQuery) -> VerifiedUserDTO:

        payload = self.token_service.decode_token(query.access_token)

        if payload.get("type") != "access":
            raise InvalidTokenError("Not an access token")

        jti = payload.get("jti")
        if not jti:
            raise InvalidTokenError("Token missing JTI")

        if await self.token_store.is_blacklisted(jti):
            raise InvalidTokenError("Token has been revoked")

        return VerifiedUserDTO(
            user_id=UUID(payload["sub"]),
            email=payload["email"],
            role=payload["role"],
        )
