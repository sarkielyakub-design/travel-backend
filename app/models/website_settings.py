from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)

from datetime import datetime

from app.db.session import Base


class WebsiteSettings(Base):
    __tablename__ = "website_settings"

    id = Column(Integer, primary_key=True, index=True)

    company_name = Column(String, nullable=False)

    company_email = Column(String, default="")

    phone_one = Column(String, default="")

    phone_two = Column(String, default="")

    address = Column(Text, default="")

    business_hours = Column(String, default="")

    logo_url = Column(String, nullable=True)

    logo_public_id = Column(String, nullable=True)

    favicon_url = Column(String, nullable=True)

    favicon_public_id = Column(String, nullable=True)

    booking_url = Column(String, default="")

    whatsapp = Column(String, default="")

    facebook = Column(String, default="")

    instagram = Column(String, default="")

    linkedin = Column(String, default="")

    twitter = Column(String, default="")

    youtube = Column(String, default="")

    tiktok = Column(String, default="")

    google_maps = Column(Text, default="")

    seo_title = Column(String, default="")

    seo_description = Column(Text, default="")

    footer_text = Column(Text, default="")

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )