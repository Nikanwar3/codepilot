"""
Aggregates all v1 routers under a single APIRouter so app.main only has to
include one object. New routers (repositories, agent runs, auth, ...) get
added here as each feature step lands — nothing else needs to change.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
