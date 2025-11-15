"""Main API router."""

from fastapi import APIRouter

from app.api.endpoints import cases, laws, analytics, conversation, summarization

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(laws.router)
api_router.include_router(cases.router)
api_router.include_router(analytics.router)
api_router.include_router(conversation.router)
api_router.include_router(summarization.router)
