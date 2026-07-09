from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
)

from datetime import datetime

from app.db.session import Base


class Hero(Base):
    __tablename__ = "hero"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    subtitle = Column(Text, default="")

    image_url = Column(String, nullable=True)

    public_id = Column(String, nullable=True)

    primary_button_text = Column(
        String,
        default="View Packages",
    )

    primary_button_link = Column(
        String,
        default="/packages",
    )

    secondary_button_text = Column(
        String,
        default="Contact Us",
    )

    secondary_button_link = Column(
        String,
        default="/contact",
    )

    booking_url = Column(
        String,
        default="https://booking.myhamdalatravels.com",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )