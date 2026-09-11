import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)


async def set_cached_url(
    short_code: str,
    original_url: str,
    expires_in_seconds: int | None = None
):
    await redis_client.set(
        f"url:{short_code}",
        original_url,
        ex=expires_in_seconds
    )


async def get_cached_url(
    short_code: str
) -> str | None:
    return await redis_client.get(
        f"url:{short_code}"
    )