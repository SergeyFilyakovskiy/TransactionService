from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.balances import router as balance_router
from app.api.v1.endpoints.currencies import router as currency_router
from app.api.v1.endpoints.reports import router as report_router
from app.api.v1.endpoints.transactions import router as transaction_router
from app.api.v1.endpoints.users import router as user_router
from app.api.v1.endpoints.verify import router as verify_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth_router)
v1_router.include_router(verify_router)
v1_router.include_router(balance_router)
v1_router.include_router(currency_router)
v1_router.include_router(transaction_router)
v1_router.include_router(user_router)
v1_router.include_router(report_router)
