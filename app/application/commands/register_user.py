from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.domain.entities import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.interfaces.i_user_repo import IUserRepo
from app.domain.value_objects import Email, HashedPassword


@dataclass
class RegisterUserCommand:
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class RegisterUserHandler:

    def __init__(self, user_repo: IUserRepo) -> None:
        self.user_repo = user_repo

    async def handle(self, command: RegisterUserCommand) -> User:

        email_vo = Email(command.email)
        password_vo = HashedPassword.from_plain(command.password)

        if await self.user_repo.exists_by_email(email_vo.value):
            raise UserAlreadyExistsError(email_vo.value)

        user = User(
            id=uuid.uuid4(),
            email=email_vo,
            hashed_password=password_vo,
        )

        await self.user_repo.save(user)

        return user
