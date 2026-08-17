from datetime import datetime

from pydantic import BaseModel, HttpUrl


class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: datetime | None = None


class URLUpdate(BaseModel):
    original_url: HttpUrl | None = None
    expires_at: datetime | None = None


class URLResponse(BaseModel):
    id: int
    short_code: str
    original_url: HttpUrl
    click_count: int
    created_at: datetime
    expires_at: datetime | None

    model_config = {
        "from_attributes": True
    }