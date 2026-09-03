from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.services.url import create_url, get_user_urls


router = APIRouter(prefix="/urls", tags=["URLs"])


@router.post(
    "",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_short_url(
    url_data: URLCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_url(
        db=db,
        user_id=current_user.id,
        original_url=str(url_data.original_url),
        expires_in_minutes=url_data.expires_in_minutes
    )


@router.get("", response_model=list[URLResponse])
async def list_urls(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_user_urls(
        db=db,
        user_id=current_user.id
    )