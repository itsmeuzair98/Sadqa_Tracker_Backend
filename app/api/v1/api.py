"""
API router for version 1 of the backend application.
Plugins covered include authentication, user management, and sadqa tracking.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, sadqa

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sadqa.router, prefix="/sadqa", tags=["sadqa"])
