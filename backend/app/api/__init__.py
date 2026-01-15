# API module - Router aggregation
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.quizzes import router as quizzes_router
from app.api.inbox import router as inbox_router
from app.api.stats import router as stats_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(quizzes_router)
api_router.include_router(inbox_router)
api_router.include_router(stats_router)
