import pytest
from datetime import datetime, timedelta, timezone

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models import URL, User
from app.core.security import create_access_token


async def create_test_user(
    db_session,
    email="redirect-test@example.com"
):
    user = User(
        email=email,
        password_hash="test-password"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


async def create_test_url(
    db_session,
    user_id,
    short_code="redir123",
    original_url="https://example.com",
    expires_at=None
):
    url = URL(
        user_id=user_id,
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at
    )

    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    return url


@pytest.mark.asyncio
async def test_redirect_to_original_url(db_session):
    user = await create_test_user(
        db_session,
        email="redirect-success@example.com"
    )

    url = await create_test_url(
        db_session,
        user.id,
        short_code="redir01",
        original_url="https://example.com"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response = await client.get(
            f"/{url.short_code}"
        )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_nonexistent_short_code():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response = await client.get(
            "/doesnotexist"
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_expired_url_returns_404(db_session):
    user = await create_test_user(
        db_session,
        email="redirect-expired@example.com"
    )

    expired_time = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )

    url = await create_test_url(
        db_session,
        user.id,
        short_code="expire01",
        original_url="https://example.com",
        expires_at=expired_time
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response = await client.get(
            f"/{url.short_code}"
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_increments_click_count(db_session):
    user = await create_test_user(
        db_session,
        email="redirect-clicks@example.com"
    )

    url = await create_test_url(
        db_session,
        user.id,
        short_code="click001",
        original_url="https://example.com"
    )

    initial_click_count = url.click_count

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response = await client.get(
            f"/{url.short_code}"
        )

    await db_session.refresh(url)

    assert response.status_code == 307
    assert url.click_count == initial_click_count + 1


@pytest.mark.asyncio
async def test_multiple_redirects_increment_click_count(db_session):
    user = await create_test_user(
        db_session,
        email="redirect-multiple@example.com"
    )

    url = await create_test_url(
        db_session,
        user.id,
        short_code="click002",
        original_url="https://example.com"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response_1 = await client.get(
            f"/{url.short_code}"
        )

        response_2 = await client.get(
            f"/{url.short_code}"
        )

    await db_session.refresh(url)

    assert response_1.status_code == 307
    assert response_2.status_code == 307
    assert url.click_count == 2


@pytest.mark.asyncio
async def test_redirect_with_valid_url_does_not_require_auth(
    db_session
):
    user = await create_test_user(
        db_session,
        email="redirect-no-auth@example.com"
    )

    url = await create_test_url(
        db_session,
        user.id,
        short_code="public01",
        original_url="https://example.com"
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False
    ) as client:

        response = await client.get(
            f"/{url.short_code}"
        )

    assert response.status_code == 307