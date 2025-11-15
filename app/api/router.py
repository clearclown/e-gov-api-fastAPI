"""Main API router."""

from fastapi import APIRouter

from app.api.endpoints import cases, laws

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(cases.router)
api_router.include_router(laws.router)
