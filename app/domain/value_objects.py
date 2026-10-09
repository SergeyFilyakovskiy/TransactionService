from __future__ import annotations

import re
from dataclasses import dataclass

import bcrypt


@dataclass(frozen=True)
class Email:

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise TypeError("Email must be a sting")
        normalized = self.value.strip().lower()
        if not re.match(r"^[\w.+-]+@[\w-]+\.[a-z]{2,}$", normalized):
            raise ValueError(f"Invalid email format: {self.value}")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class HashedPassword:

    value: str

    @staticmethod
    def from_plain(plain: str) -> HashedPassword:
        if len(plain) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(plain) > 128:
            raise ValueError("Password is too long")
        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt())
        return HashedPassword(hashed.decode())

    @staticmethod
    def from_hash(hashed: str) -> HashedPassword:
        return HashedPassword(hashed)

    def verify(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode(), self.value.encode())

    def __repr__(self) -> str:
        return "HashedPassword(value=***)"


@dataclass
class UserProfile:
    """value-object for entity User"""

    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def full_name(self) -> str | None:

        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return None
