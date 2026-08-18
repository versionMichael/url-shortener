from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def register_user(
        db: AsyncSession,
        email: str,
        password: str
) -> User:
    existing_user = await db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> User | None:
    user = await db.scalar(
        select(User).where(User.email == email)
    )

    if not user or not verify_password(password, user.password_hash):
        return None

    return user