import pytest
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from app.models import URL, User
from app.main import app
from app.core.security import create_access_token


async def create_test_user(
    db_session,
    email="urltest@example.com"
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
    short_code="test123",
    original_url="https://example.com"
):
    url = URL(
        user_id=user_id,
        short_code=short_code,
        original_url=original_url
    )

    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    return url


@pytest.mark.asyncio
async def test_create_url(db_session):
    user = await create_test_user(db_session)

    url = await create_test_url(
        db_session,
        user.id
    )

    result = await db_session.get(
        URL,
        url.id
    )

    assert result is not None
    assert result.short_code == "test123"
    assert result.original_url == "https://example.com"
    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_get_url_by_id(db_session):
    user = await create_test_user(db_session)

    url = await create_test_url(
        db_session,
        user.id,
        short_code="get123"
    )

    result = await db_session.get(
        URL,
        url.id
    )

    assert result is not None
    assert result.id == url.id
    assert result.short_code == "get123"


@pytest.mark.asyncio
async def test_get_url_by_short_code(db_session):
    user = await create_test_user(db_session)

    url = await create_test_url(
        db_session,
        user.id,
        short_code="find123"
    )

    result = await db_session.scalar(
        select(URL).where(
            URL.short_code == "find123"
        )
    )

    assert result is not None
    assert result.id == url.id
    assert result.original_url == "https://example.com"


@pytest.mark.asyncio
async def test_delete_url(db_session):
    user = await create_test_user(db_session)

    url = await create_test_url(
        db_session,
        user.id,
        short_code="del123"
    )

    await db_session.delete(url)
    await db_session.commit()

    result = await db_session.get(
        URL,
        url.id
    )

    assert result is None


@pytest.mark.asyncio
async def test_url_belongs_to_user(db_session):
    user = await create_test_user(db_session)

    url = await create_test_url(
        db_session,
        user.id,
        short_code="owner123"
    )

    result = await db_session.get(
        URL,
        url.id
    )

    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_duplicate_short_code_rejected(db_session):
    user = await create_test_user(db_session)

    await create_test_url(
        db_session,
        user.id,
        short_code="dupe123"
    )

    duplicate_url = URL(
        user_id=user.id,
        short_code="dupe123",
        original_url="https://different.com"
    )

    db_session.add(duplicate_url)

    with pytest.raises(Exception):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_create_url_endpoint(db_session):
    user = await create_test_user(
        db_session,
        email="create-endpoint@example.com"
    )

    token = create_access_token(user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/urls",
            json={
                "original_url": "https://example.com"
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 201
    assert "short_code" in response.json()


@pytest.mark.asyncio
async def test_get_urls_endpoint(db_session):
    user = await create_test_user(
        db_session,
        email="get-urls@example.com"
    )

    token = create_access_token(user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.get(
            "/urls",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_url_by_id_endpoint(db_session):
    user = await create_test_user(
        db_session,
        email="get-url-endpoint@example.com"
    )

    token = create_access_token(user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        create_response = await client.post(
            "/urls",
            json={
                "original_url": "https://example.com"
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        url_id = create_response.json()["id"]

        response = await client.get(
            f"/urls/{url_id}",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 200
    assert response.json()["id"] == url_id


@pytest.mark.asyncio
async def test_cannot_access_another_users_url(db_session):
    owner = await create_test_user(
        db_session,
        email="owner@example.com"
    )

    other_user = await create_test_user(
        db_session,
        email="other@example.com"
    )

    owner_token = create_access_token(owner.id)
    other_user_token = create_access_token(other_user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        create_response = await client.post(
            "/urls",
            json={
                "original_url": "https://example.com"
            },
            headers={
                "Authorization": f"Bearer {owner_token}"
            }
        )

        url_id = create_response.json()["id"]

        response = await client.get(
            f"/urls/{url_id}",
            headers={
                "Authorization": f"Bearer {other_user_token}"
            }
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_url_endpoint(db_session):
    user = await create_test_user(
        db_session,
        email="delete-endpoint@example.com"
    )

    token = create_access_token(user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        create_response = await client.post(
            "/urls",
            json={
                "original_url": "https://example.com"
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        url_id = create_response.json()["id"]

        response = await client.delete(
            f"/urls/{url_id}",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_cannot_delete_another_users_url(db_session):
    owner = await create_test_user(
        db_session,
        email="delete-owner@example.com"
    )

    other_user = await create_test_user(
        db_session,
        email="delete-other@example.com"
    )

    owner_token = create_access_token(owner.id)
    other_user_token = create_access_token(other_user.id)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        create_response = await client.post(
            "/urls",
            json={
                "original_url": "https://example.com"
            },
            headers={
                "Authorization": f"Bearer {owner_token}"
            }
        )

        url_id = create_response.json()["id"]

        response = await client.delete(
            f"/urls/{url_id}",
            headers={
                "Authorization": f"Bearer {other_user_token}"
            }
        )

    assert response.status_code == 404