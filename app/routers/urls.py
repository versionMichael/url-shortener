from fastapi import APIRouter, Depends,HTTPException ,status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.services.url import create_url, delete_url , get_user_url ,get_user_urls


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

@router.get("/{url_id}", response_model=URLResponse)
async def get_url(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    url = await get_user_url(
        db=db,
        url_id=url_id,
        user_id=current_user.id
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    return url


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    deleted = await delete_url(
        db=db,
        url_id=url_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )