# API module - Router aggregation
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.quizzes import router as quizzes_router
from app.api.inbox import router as inbox_router
from app.api.stats import router as stats_router
from app.api.sync import router as sync_router
from app.api.decks import router as decks_router
from app.api.study import router as study_router
from app.api.deps import get_current_user, get_current_active_user

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(quizzes_router)
api_router.include_router(inbox_router)
api_router.include_router(stats_router)
api_router.include_router(sync_router)
api_router.include_router(decks_router)
api_router.include_router(study_router)
from app.api.sources import router as sources_router
api_router.include_router(sources_router)
from app.api.paper import router as paper_router
api_router.include_router(paper_router)

