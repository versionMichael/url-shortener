import pytest
from sqlalchemy import select

from app.models import User


@pytest.mark.asyncio
async def test_database_isolation_create(db_session):
    user = User(
        email="isolation@example.com",
        password_hash="test-password"
    )

    db_session.add(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_database_isolation_clean(db_session):
    result = await db_session.scalar(
        select(User).where(
            User.email == "isolation@example.com"
        )
    )

    assert result is None