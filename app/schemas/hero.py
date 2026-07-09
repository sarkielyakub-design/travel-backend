from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HeroBase(BaseModel):
    title: str
    subtitle: str = ""
    primary_button_text: str
    primary_button_link: str
    secondary_button_text: str
    secondary_button_link: str
    booking_url: str


class HeroResponse(HeroBase):
    id: int
    image_url: Optional[str] = None
    public_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True