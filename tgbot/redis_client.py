from __future__ import annotations

import json
from typing import Optional

from redis.asyncio import Redis

from tgbot.config import settings

_redis: Optional[Redis] = None


async def init_redis() -> Redis:
    global _redis
    _redis = Redis.from_url(settings.REDIS_URL, decode_responses=False)
    return _redis


async def close_redis() -> None:
    if _redis:
        await _redis.aclose()


def get_redis() -> Redis:
    assert _redis is not None, "Redis is not initialised"
    return _redis


# --- user_status ---

async def get_user_status(user_id: int) -> str:
    val = await get_redis().get(f"user_status:{user_id}")
    return val.decode() if val else "None"


async def set_user_status(user_id: int, status: str, ttl: int = 3600) -> None:
    await get_redis().setex(f"user_status:{user_id}", ttl, status)


async def del_user_status(user_id: int) -> None:
    await get_redis().delete(f"user_status:{user_id}")


# --- generic cache ---

async def get_cache(key: str) -> Optional[dict | list]:
    val = await get_redis().get(f"cache:{key}")
    return json.loads(val) if val else None


async def set_cache(key: str, value: dict | list, ttl: int) -> None:
    await get_redis().setex(f"cache:{key}", ttl, json.dumps(value))
