from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.services.cache import get_cached_url, set_cached_url
from app.services.url import get_url_by_code, increment_click_count



router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    db: AsyncSession = Depends(get_db)
):

    cached_url = await get_cached_url(short_code)

    if cached_url:
        await increment_click_count(
            db=db,
            short_code=short_code
        )

        return RedirectResponse(
            url=cached_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    
    url = await get_url_by_code(
        db=db,
        short_code=short_code
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found or has expired"
        )

    await increment_click_count(
        db=db,
        short_code=short_code
)

    expires_in_seconds = None

    if url.expires_at:
        expires_in_seconds = int(
            (url.expires_at - datetime.now(timezone.utc)).total_seconds()
        )

    await set_cached_url(
        short_code,
        str(url.original_url),
        expires_in_seconds
    )

    return RedirectResponse(
        url=str(url.original_url),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )