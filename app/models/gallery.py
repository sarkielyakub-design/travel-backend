from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)

from datetime import datetime

from app.db.session import Base


class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    category = Column(
        String,
        default="General",
    )

    image_url = Column(
        String,
        nullable=False,
    )

    public_id = Column(
        String,
        nullable=False,
    )

    featured = Column(
        Boolean,
        default=False,
    )

    active = Column(
        Boolean,
        default=True,
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