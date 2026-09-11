import os
import asyncio

from dotenv import load_dotenv

from sqlalchemy import delete

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

import pytest_asyncio

from app.database import Base
from app.models import URL, User
from app.main import app
from app.core.dependencies import get_db


def pytest_asyncio_loop_factories(config, item):
    return {
        "selector": asyncio.SelectorEventLoop
    }


load_dotenv()


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)


test_engine = create_async_engine(
    TEST_DATABASE_URL
)


TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

        await session.rollback()

        await session.execute(
            delete(URL)
        )

        await session.execute(
            delete(User)
        )

        await session.commit()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    yield

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def override_database():
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()