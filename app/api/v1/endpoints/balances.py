from uuid import UUID

from fastapi import APIRouter

from app.api.v1.schemas.balance import BalanceResponse
from app.application.queries.get_balance import GetBalanceQuery
from app.application.queries.list_balances import ListBalancesQuery
from app.core.dependencies import (
    AccessTokenDep,
    GetBalanceHandlerDep,
    ListBalancesHandlerDep,
    TokenServiceDep,
)

router = APIRouter(prefix="/balances", tags=["Balances"])


@router.get("", response_model=list[BalanceResponse])
async def list_balances(
    handler: ListBalancesHandlerDep,
    token_service: TokenServiceDep,
    access_token: AccessTokenDep,
    currency_id: UUID | None = None,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    balances = await handler.execute(
        ListBalancesQuery(user_id=user_id, currency_id=currency_id)
    )
    return balances


@router.get("/{currency_id}", response_model=BalanceResponse)
async def get_balance(
    currency_id: UUID,
    access_token: AccessTokenDep,
    handler: GetBalanceHandlerDep,
    token_service: TokenServiceDep,
):
    payload = token_service.decode_token(access_token)
    user_id = UUID(payload["sub"])

    balance = await handler.execute(
        GetBalanceQuery(user_id=user_id, currency_id=currency_id)
    )
    return balance
