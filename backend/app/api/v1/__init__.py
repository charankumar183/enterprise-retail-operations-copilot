from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.products import router as products_router
from backend.app.api.v1.inventory import router as inventory_router
from backend.app.api.v1.documents import router as documents_router
from backend.app.api.v1.reports import router as reports_router
from backend.app.api.v1.feedback import router as feedback_router
from backend.app.api.v1.evaluation import router as evaluation_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(documents_router)
api_router.include_router(reports_router)
api_router.include_router(feedback_router)
api_router.include_router(evaluation_router)
