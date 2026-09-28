# API routes package
from fastapi import APIRouter

from .routes import cases_router, presets_router

# Main API router
api_router = APIRouter(prefix="/api", tags=["api"])
api_router.include_router(cases_router.router)
api_router.include_router(presets_router.router)

__all__ = ["api_router"]
