from fastapi import APIRouter
from app.api.v1 import auth, subscriptions, snapshots, knowledge_bases, cards, gulp

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router)
api_router.include_router(subscriptions.router)
api_router.include_router(snapshots.router)
api_router.include_router(knowledge_bases.router)
api_router.include_router(cards.router)
api_router.include_router(gulp.router)
