from fastapi import APIRouter

from . import (
    rights,
    users
)


api_router = APIRouter(prefix="/admin")
api_router.include_router(users.router)
api_router.include_router(rights.router)
