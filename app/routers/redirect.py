from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.url import get_url_by_code


router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):
    url = await get_url_by_code(
        db=db,
        short_code=short_code
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found or has expired"
        )

    return RedirectResponse(
        url=str(url.original_url),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )