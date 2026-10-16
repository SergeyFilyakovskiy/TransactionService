from uuid import UUID

from fastapi import APIRouter, Query

from app.api.v1.schemas.transaction import (
    CancelTransactionRequest,
    DepositRequest,
    TransactionResponse,
    WithdrawRequest,
)
from app.application.commands.cancel_transaction import CancelTransactionCommand
from app.application.commands.deposit_funds import DepositFundsCommand
from app.application.commands.withdraw_funds import WithdrawFundsCommand
from app.application.queries.get_transaction import GetTransactionQuery
from app.application.queries.list_transactions import ListTransactionsQuery
from app.core.dependencies import (
    AccessTokenDep,
    CancelTransactionHandlerDep,
    DepositHandlerDep,
    GetTransactionHandlerDep,
    ListTransactionsHandlerDep,
    TokenServiceDep,
    WithdrawHandlerDep,
)
from app.core.enums import TransactionStatus, TransactionType

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse)
async def deposit(
    body: DepositRequest,
    access_token: AccessTokenDep,
    handler: DepositHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    transaction = await handler.execute(
        DepositFundsCommand(
            user_id=user_id,
            currency_id=body.currency_id,
            amount=body.amount,
        )
    )
    return transaction


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw(
    body: WithdrawRequest,
    access_token: AccessTokenDep,
    handler: WithdrawHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    transaction = await handler.execute(
        WithdrawFundsCommand(
            user_id=user_id,
            currency_id=body.currency_id,
            amount=body.amount,
        )
    )
    return transaction


@router.post("/cancel", response_model=TransactionResponse)
async def cancel_transaction(
    body: CancelTransactionRequest,
    access_token: AccessTokenDep,
    handler: CancelTransactionHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    transaction = await handler.execute(
        CancelTransactionCommand(
            transaction_id=body.transaction_id,
            cancelled_by_user_id=user_id,
        )
    )
    return transaction


@router.get("", response_model=list[TransactionResponse])
async def list_transactions(
    access_token: AccessTokenDep,
    handler: ListTransactionsHandlerDep,
    token_service: TokenServiceDep,
    currency_id: UUID | None = None,
    status: TransactionStatus | None = None,
    type: TransactionType | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    transactions = await handler.execute(
        ListTransactionsQuery(
            user_id=user_id,
            currency_id=currency_id,
            status=status,
            transaction_type=type,
            limit=limit,
            offset=offset,
        )
    )
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    access_token: AccessTokenDep,
    handler: GetTransactionHandlerDep,
    token_service: TokenServiceDep,
):
    transaction = await handler.execute(
        GetTransactionQuery(transaction_id=transaction_id)
    )
    return transaction
