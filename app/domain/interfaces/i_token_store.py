from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class ITokenStore(ABC):

    # ── Refresh tokens ────────────────────────────────────

    @abstractmethod
    async def save_refresh_token(
        self,
        user_id: UUID,
        token: str,
        ttl: int,  # sec
    ) -> None:
        """Save refresh token with TTL"""
        ...

    @abstractmethod
    async def get_refresh_token(self, user_id: UUID) -> str | None:
        """Get user refresh token"""
        ...

    @abstractmethod
    async def delete_refresh_token(self, user_id: UUID) -> None:
        """Delete refresh token (logout / rotation)"""
        ...

    @abstractmethod
    async def refresh_token_exists(self, user_id: UUID, token: str) -> bool: ...

    # ── Blacklist access tokens ───────────────────────────

    @abstractmethod
    async def blacklist_token(
        self,
        jti: str,
        ttl: int,
    ) -> None: ...

    @abstractmethod
    async def is_blacklisted(self, jti: str) -> bool: ...

    # ── Failed login attempts (brute-force protection) ────

    @abstractmethod
    async def increment_failed_attempts(
        self,
        email: str,
        ttl: int,
    ) -> int: ...

    @abstractmethod
    async def get_failed_attempts(self, email: str) -> int: ...

    @abstractmethod
    async def reset_failed_attempts(self, email: str) -> None: ...
