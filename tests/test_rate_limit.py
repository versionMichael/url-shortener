import pytest

from app.services.rate_limit import (
    check_rate_limit,
    redis_client
)


@pytest.mark.asyncio
async def test_rate_limit():
    ip_address = "test-rate-limit"

    await redis_client.delete(
        f"rate_limit:{ip_address}"
    )

    for _ in range(10):
        assert await check_rate_limit(ip_address) is True

    assert await check_rate_limit(ip_address) is False

    await redis_client.delete(
        f"rate_limit:{ip_address}"
    )

    await redis_client.aclose()


@pytest.mark.asyncio
async def test_rate_limit_sets_ttl():
    ip_address = "test-rate-limit-ttl"

    await redis_client.delete(
        f"rate_limit:{ip_address}"
    )

    await check_rate_limit(ip_address)

    ttl = await redis_client.ttl(
        f"rate_limit:{ip_address}"
    )

    assert 0 < ttl <= 60

    await redis_client.delete(
        f"rate_limit:{ip_address}"
    )

    await redis_client.aclose()