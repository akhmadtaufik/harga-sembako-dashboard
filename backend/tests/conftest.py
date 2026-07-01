import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.coder import PickleCoder
from redis import asyncio as aioredis

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_cache():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=False)
    FastAPICache.init(RedisBackend(redis), prefix="sembako-cache", coder=PickleCoder)
    yield
    await redis.close()

@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def auth_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Dynamically inject API key from settings
        client.headers.update({"X-API-Key": settings.API_KEY})
        yield client
