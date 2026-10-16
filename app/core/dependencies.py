from __future__ import annotations

from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands import (
    CancelTransactionHandler,
    CreateCurrencyHandler,
    DeleteCurrencyHandler,
    DepositFundsHandler,
    FreezeUserHandler,
    GenerateReportHandler,
    LoginUserHandler,
    LogoutUserHandler,
    RefreshTokenHandler,
    RegisterUserHandler,
    UnfreezeUserHandler,
    UpdateCurrencyHandler,
    WithdrawFundsHandler,
)
from app.application.queries import (
    GetBalanceHandler,
    GetCurrencyHandler,
    GetReportHandler,
    GetTransactionHandler,
    GetUserHandler,
    ListBalancesHandler,
    ListCurrenciesHandler,
    ListTransactionsHandler,
    VerifyTokenHandler,
)
from app.application.services.token_service import TokenService
from app.infrastructure.postgres.repositories import (
    BalanceRepository,
    CurrencyRepository,
    ReportFileRepository,
    TransactionRepository,
    UserRepository,
)
from app.infrastructure.postgres.session import async_session
from app.infrastructure.redis.token_store import RedisTokenStore

bearer_scheme = HTTPBearer(auto_error=False)


# ── Core dependencies ─────────────────────────────────────


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


async def get_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    return credentials.credentials


# ── Repository dependencies ──────────────────────────────


async def get_user_repo(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
) -> UserRepository:
    return UserRepository(session)


async def get_currency_repo(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
) -> CurrencyRepository:
    return CurrencyRepository(session)


async def get_balance_repo(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
) -> BalanceRepository:
    return BalanceRepository(session)


async def get_transaction_repo(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
) -> TransactionRepository:
    return TransactionRepository(session)


async def get_report_repo(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
) -> ReportFileRepository:
    return ReportFileRepository(session)


# ── Service dependencies ─────────────────────────────────


async def get_token_store(
    redis=Depends(get_redis),
) -> RedisTokenStore:
    return RedisTokenStore(redis)


async def get_token_service() -> TokenService:
    return TokenService()


# ── Command handlers ─────────────────────────────────────


async def get_register_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
) -> RegisterUserHandler:
    return RegisterUserHandler(session, user_repo, currency_repo, balance_repo)


async def get_login_handler(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    token_store: Annotated[RedisTokenStore, Depends(get_token_store)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LoginUserHandler:
    return LoginUserHandler(user_repo, token_store, token_service)


async def get_refresh_handler(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    token_store: Annotated[RedisTokenStore, Depends(get_token_store)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> RefreshTokenHandler:
    return RefreshTokenHandler(user_repo, token_store, token_service)


async def get_logout_handler(
    token_store: Annotated[RedisTokenStore, Depends(get_token_store)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LogoutUserHandler:
    return LogoutUserHandler(token_store, token_service)


async def get_create_currency_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
) -> CreateCurrencyHandler:
    return CreateCurrencyHandler(session, currency_repo)


async def get_update_currency_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
) -> UpdateCurrencyHandler:
    return UpdateCurrencyHandler(session, currency_repo)


async def get_delete_currency_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
) -> DeleteCurrencyHandler:
    return DeleteCurrencyHandler(session, currency_repo)


async def get_deposit_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repo)],
) -> DepositFundsHandler:
    return DepositFundsHandler(
        session, user_repo, balance_repo, currency_repo, transaction_repo
    )


async def get_withdraw_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repo)],
) -> WithdrawFundsHandler:
    return WithdrawFundsHandler(
        session, user_repo, balance_repo, currency_repo, transaction_repo
    )


async def get_cancel_transaction_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repo)],
) -> CancelTransactionHandler:
    return CancelTransactionHandler(session, user_repo, balance_repo, transaction_repo)


async def get_freeze_user_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> FreezeUserHandler:
    return FreezeUserHandler(session, user_repo)


async def get_unfreeze_user_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UnfreezeUserHandler:
    return UnfreezeUserHandler(session, user_repo)


async def get_generate_report_handler(
    session: Annotated[AsyncSession, Depends(get_postgres_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    report_repo: Annotated[ReportFileRepository, Depends(get_report_repo)],
) -> GenerateReportHandler:
    return GenerateReportHandler(session, user_repo, report_repo)


# ── Query handlers ───────────────────────────────────────


async def get_verify_handler(
    token_store: Annotated[RedisTokenStore, Depends(get_token_store)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> VerifyTokenHandler:
    return VerifyTokenHandler(token_store, token_service)


async def get_get_currency_handler(
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
) -> GetCurrencyHandler:
    return GetCurrencyHandler(currency_repo)


async def get_list_currencies_handler(
    currency_repo: Annotated[CurrencyRepository, Depends(get_currency_repo)],
) -> ListCurrenciesHandler:
    return ListCurrenciesHandler(currency_repo)


async def get_get_balance_handler(
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
) -> GetBalanceHandler:
    return GetBalanceHandler(balance_repo)


async def get_list_balances_handler(
    balance_repo: Annotated[BalanceRepository, Depends(get_balance_repo)],
) -> ListBalancesHandler:
    return ListBalancesHandler(balance_repo)


async def get_get_transaction_handler(
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repo)],
) -> GetTransactionHandler:
    return GetTransactionHandler(transaction_repo)


async def get_list_transactions_handler(
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repo)],
) -> ListTransactionsHandler:
    return ListTransactionsHandler(transaction_repo)


async def get_get_report_handler(
    report_repo: Annotated[ReportFileRepository, Depends(get_report_repo)],
) -> GetReportHandler:
    return GetReportHandler(report_repo)


async def get_get_user_handler(
    user_repo: UserRepoDep,
) -> GetUserHandler:
    return GetUserHandler(user_repo)


# ── Type aliases for use in endpoints ────────────────────

SessionDep = Annotated[AsyncSession, Depends(get_postgres_session)]
AccessTokenDep = Annotated[str, Depends(get_access_token)]

UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
CurrencyRepoDep = Annotated[CurrencyRepository, Depends(get_currency_repo)]
BalanceRepoDep = Annotated[BalanceRepository, Depends(get_balance_repo)]
TransactionRepoDep = Annotated[TransactionRepository, Depends(get_transaction_repo)]
ReportRepoDep = Annotated[ReportFileRepository, Depends(get_report_repo)]

TokenStoreDep = Annotated[RedisTokenStore, Depends(get_token_store)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]

RegisterHandlerDep = Annotated[RegisterUserHandler, Depends(get_register_handler)]
LoginHandlerDep = Annotated[LoginUserHandler, Depends(get_login_handler)]
RefreshHandlerDep = Annotated[RefreshTokenHandler, Depends(get_refresh_handler)]
LogoutHandlerDep = Annotated[LogoutUserHandler, Depends(get_logout_handler)]
VerifyHandlerDep = Annotated[VerifyTokenHandler, Depends(get_verify_handler)]

CreateCurrencyHandlerDep = Annotated[
    CreateCurrencyHandler, Depends(get_create_currency_handler)
]
UpdateCurrencyHandlerDep = Annotated[
    UpdateCurrencyHandler, Depends(get_update_currency_handler)
]
DeleteCurrencyHandlerDep = Annotated[
    DeleteCurrencyHandler, Depends(get_delete_currency_handler)
]

DepositHandlerDep = Annotated[DepositFundsHandler, Depends(get_deposit_handler)]
WithdrawHandlerDep = Annotated[WithdrawFundsHandler, Depends(get_withdraw_handler)]
CancelTransactionHandlerDep = Annotated[
    CancelTransactionHandler, Depends(get_cancel_transaction_handler)
]

FreezeUserHandlerDep = Annotated[FreezeUserHandler, Depends(get_freeze_user_handler)]
UnfreezeUserHandlerDep = Annotated[
    UnfreezeUserHandler, Depends(get_unfreeze_user_handler)
]

GenerateReportHandlerDep = Annotated[
    GenerateReportHandler, Depends(get_generate_report_handler)
]

GetCurrencyHandlerDep = Annotated[GetCurrencyHandler, Depends(get_get_currency_handler)]
ListCurrenciesHandlerDep = Annotated[
    ListCurrenciesHandler, Depends(get_list_currencies_handler)
]

GetBalanceHandlerDep = Annotated[GetBalanceHandler, Depends(get_get_balance_handler)]
ListBalancesHandlerDep = Annotated[
    ListBalancesHandler, Depends(get_list_balances_handler)
]

GetTransactionHandlerDep = Annotated[
    GetTransactionHandler, Depends(get_get_transaction_handler)
]
ListTransactionsHandlerDep = Annotated[
    ListTransactionsHandler, Depends(get_list_transactions_handler)
]

GetReportHandlerDep = Annotated[GetReportHandler, Depends(get_get_report_handler)]

GetUserHandlerDep = Annotated[GetUserHandler, Depends(get_get_user_handler)]
