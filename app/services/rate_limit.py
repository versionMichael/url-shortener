import redis.asyncio as redis

from app.core.config import settings


redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True
)


RATE_LIMIT = 10
WINDOW_SECONDS = 60

async def check_rate_limit(
        ip_address: str
) -> bool:
    key = f"rate_limit:{ip_address}"

    count = await redis_client.incr(key)

    if count == 1:
        await redis_client.expire(
            key,
            WINDOW_SECONDS
        )

    return count <= RATE_LIMIT