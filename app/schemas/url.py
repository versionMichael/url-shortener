from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_in_minutes: int | None = Field(
        default=None,
        ge=1,
        description="How many minutes until the URL expires. Leave empty for no expiration."
    )


class URLUpdate(BaseModel):
    original_url: HttpUrl | None = None
    expires_in_minutes: int | None = Field(
        default=None,
        ge=1,
        description="How many minutes until the URL expires. Leave empty for no expiration."
    )


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