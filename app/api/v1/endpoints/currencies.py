from uuid import UUID

from fastapi import APIRouter, status

from app.api.v1.schemas.currency import (
    CurrencyCreateRequest,
    CurrencyResponse,
    CurrencyUpdateRequest,
)
from app.application.commands.create_currency import CreateCurrencyCommand
from app.application.commands.delete_currency import DeleteCurrencyCommand
from app.application.commands.update_currency import UpdateCurrencyCommand
from app.application.queries.get_currency import GetCurrencyQuery
from app.application.queries.list_currencies import ListCurrenciesQuery
from app.core.dependencies import (
    CreateCurrencyHandlerDep,
    DeleteCurrencyHandlerDep,
    GetCurrencyHandlerDep,
    ListCurrenciesHandlerDep,
    UpdateCurrencyHandlerDep,
)

router = APIRouter(prefix="/currencies", tags=["Currencies"])


@router.post(
    "",
    response_model=CurrencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_currency(
    body: CurrencyCreateRequest,
    handler: CreateCurrencyHandlerDep,
):
    currency = await handler.execute(
        CreateCurrencyCommand(code=body.code, name=body.name)
    )
    return currency


@router.get("", response_model=list[CurrencyResponse])
async def list_currencies(
    handler: ListCurrenciesHandlerDep,
    limit: int = 100,
    offset: int = 0,
):
    currencies = await handler.execute(ListCurrenciesQuery(limit=limit, offset=offset))
    return currencies


@router.get("/{currency_id}", response_model=CurrencyResponse)
async def get_currency(
    currency_id: UUID,
    handler: GetCurrencyHandlerDep,
):
    currency = await handler.execute(GetCurrencyQuery(currency_id=currency_id))
    return currency


@router.patch("/{currency_id}", response_model=CurrencyResponse)
async def update_currency(
    currency_id: UUID,
    body: CurrencyUpdateRequest,
    handler: UpdateCurrencyHandlerDep,
):
    currency = await handler.execute(
        UpdateCurrencyCommand(currency_id=currency_id, name=body.name)
    )
    return currency


@router.delete("/{currency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_currency(
    currency_id: UUID,
    handler: DeleteCurrencyHandlerDep,
):
    await handler.execute(DeleteCurrencyCommand(currency_id=currency_id))
