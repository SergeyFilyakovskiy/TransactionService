import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Balance, User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.interfaces import IBalanceRepo, ICurrencyRepo, IUserRepo
from app.domain.value_objects import Email, HashedPassword


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    plain_password: str


class RegisterUserHandler:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: IUserRepo,
        currency_repo: ICurrencyRepo,
        balance_repo: IBalanceRepo,
    ):
        self.session = session
        self.user_repo = user_repo
        self.currency_repo = currency_repo
        self.balance_repo = balance_repo

    async def execute(self, command: RegisterUserCommand) -> User:
        if await self.user_repo.exists_by_email(command.email):
            raise UserAlreadyExistsError(command.email)

        user = User(
            id=uuid.uuid4(),
            email=Email(command.email),
            hashed_password=HashedPassword.from_plain(command.plain_password),
            is_frozen=False,
        )

        await self.user_repo.save(user)

        currencies = await self.currency_repo.list()

        for currency in currencies:
            balance = Balance.create(
                user_id=user.id,
                currency_id=currency.id,
                amount=Decimal("0"),
            )
            await self.balance_repo.save(balance)

        await self.session.commit()

        return user
