import pytest

from app.services.cache import (
    set_cached_url,
    get_cached_url,
    redis_client
)


@pytest.mark.asyncio
async def test_set_and_get_cached_url():
    short_code = "test123"
    original_url = "https://example.com"

    await set_cached_url(
        short_code,
        original_url
    )

    result = await get_cached_url(short_code)

    assert result == original_url

    await redis_client.delete(
        f"url:{short_code}"
    )

    await redis_client.aclose()

@pytest.mark.asyncio
async def test_delete_cached_url():
    short_code = "delete123"
    original_url = "https://example.com"

    await set_cached_url(
        short_code,
        original_url
    )

    await redis_client.delete(
        f"url:{short_code}"
    )

    result = await get_cached_url(short_code)

    assert result is None

    await redis_client.aclose()

@pytest.mark.asyncio
async def test_cached_url_ttl():
    short_code = "ttl123"
    original_url = "https://example.com"

    await set_cached_url(
        short_code,
        original_url,
        expires_in_seconds=60
    )

    ttl = await redis_client.ttl(
        f"url:{short_code}"
    )

    assert 0 < ttl <= 60

    await redis_client.delete(
        f"url:{short_code}"
    )

    await redis_client.aclose()