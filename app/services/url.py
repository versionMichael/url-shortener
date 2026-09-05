from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL


def generate_short_code(length: int = 8) -> str:
    return secrets.token_urlsafe(length)[:length]


async def create_url(
    db: AsyncSession,
    user_id: int,
    original_url: str,
    expires_in_minutes: int | None = None
) -> URL:
    while True:
        short_code = generate_short_code()

        existing_url = await db.scalar(
            select(URL).where(URL.short_code == short_code)
        )

        if not existing_url:
            break

    expires_at = None

    if expires_in_minutes is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=expires_in_minutes
        )

    url = URL(
        user_id=user_id,
        short_code=short_code,
        original_url=original_url,
        expires_at=expires_at
    )

    db.add(url)
    await db.commit()
    await db.refresh(url)

    return url


async def get_user_urls(
    db: AsyncSession,
    user_id: int
) -> list[URL]:
    result = await db.scalars(
        select(URL)
        .where(URL.user_id == user_id)
        .order_by(URL.created_at.desc())
    )

    return list(result)

async def get_user_url(
        db: AsyncSession,
        url_id: int,
        user_id: int
) -> URL | None:
    return await db.scalar(
        select(URL).where(
            URL.id == url_id,
            URL.user_id == user_id
        )
    )


async def delete_url(
        db: AsyncSession,
        url_id: int,
        user_id: int
) -> bool:
    url = await get_user_url(
        db=db,
        url_id=url_id,
        user_id=user_id
    )

    if not url:
        return False

    await db.delete(url)
    await db.commit()

    return True


async def get_url_by_code(
    db: AsyncSession,
    short_code: str
) -> URL | None:
    url = await db.scalar(
        select(URL).where(URL.short_code == short_code)
    )

    if not url:
        return None

    if url.expires_at and url.expires_at <= datetime.now(timezone.utc):
        return None

    url.click_count += 1

    await db.commit()

    return url