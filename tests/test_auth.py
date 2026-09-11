import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.post(
            "/auth/register",
            json={
                "email": "auth-test-3@example.com",
                "password": "password123"
            }
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "auth-test-3@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_user():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )

        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123"
            }
        )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        await client.post(
            "/auth/register",
            json={
                "email": "login-test@example.com",
                "password": "password123"
            }
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "login-test@example.com",
                "password": "password123"
            }
        )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        await client.post(
            "/auth/register",
            json={
                "email": "wrong-password@example.com",
                "password": "password123"
            }
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "wrong-password@example.com",
                "password": "wrongpassword"
            }
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.get("/urls")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:

        response = await client.get(
            "/urls",
            headers={
                "Authorization": "Bearer invalid-token"
            }
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED