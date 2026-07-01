from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.coder import PickleCoder
from redis import asyncio as aioredis
from app.core.config import settings
from app.core.exceptions import (
    UnauthorizedException,
    unauthorized_exception_handler,
    sqlalchemy_exception_handler,
    dbapi_exception_handler,
    global_exception_handler,
)
from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(DBAPIError, dbapi_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="sembako-cache", coder=PickleCoder)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Include the API router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
