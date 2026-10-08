from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.domain.value_objects import Email, HashedPassword


@dataclass
class User:

    id: UUID
    email: Email
    hashed_password: HashedPassword
    is_frozen: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def change_email(self, new_email: str) -> None:
        object.__setattr__(self, "email", Email(new_email))

    def verify_password(self, plain: str) -> bool:
        if self.hashed_password is None:
            return False
        return self.hashed_password.verify(plain)

    def froze(self) -> None:
        self.is_frozen = True
        self.updated_at = datetime.now(timezone.utc)
