from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from config import config
from fastapi import (
    FastAPI,
    Request,
    status
)
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from routers import api_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend())
    yield None


app = FastAPI()
app.include_router(api_router)


@app.middleware("http")
async def is_authorized_intreface(request: Request, call_next):
    if request.headers.get("app-auth-token") != config.BF_ACCESS_KEY:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Wrong access token."})
    return await call_next(request)

if __name__ == "__main__":
    from utils.init import init_application
    init_application(app)
