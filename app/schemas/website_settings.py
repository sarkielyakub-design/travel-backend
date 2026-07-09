from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WebsiteSettingsResponse(BaseModel):

    id: int

    company_name: str

    company_email: str

    phone_one: str

    phone_two: str

    address: str

    business_hours: str

    logo_url: Optional[str] = None

    favicon_url: Optional[str] = None

    booking_url: str

    whatsapp: str

    facebook: str

    instagram: str

    linkedin: str

    twitter: str

    youtube: str

    tiktok: str

    google_maps: str

    seo_title: str

    seo_description: str

    footer_text: str

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True