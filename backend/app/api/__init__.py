from fastapi import APIRouter
from .auth import router as auth_router
from .products import router as products_router
from .discounts import router as discounts_router
from .orders import router as orders_router
from .telegram import router as telegram_router
from .uploads import router as uploads_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(discounts_router, prefix="/discounts", tags=["discounts"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(telegram_router, prefix="/telegram", tags=["telegram"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
