from fastapi import APIRouter

from . import admin


api_router = APIRouter(prefix="/api")
api_router.include_router(admin.api_router)
