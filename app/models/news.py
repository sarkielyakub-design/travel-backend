from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
)

from datetime import datetime

from app.db.session import Base


class News(Base):
    __tablename__ = "news"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    slug = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    summary = Column(
        Text,
        default="",
    )

    content = Column(
        Text,
        default="",
    )

    category = Column(
        String,
        default="General",
    )

    image_url = Column(
        String,
        nullable=True,
    )

    public_id = Column(
        String,
        nullable=True,
    )

    featured = Column(
        Boolean,
        default=False,
    )

    published = Column(
        Boolean,
        default=True,
    )

    views = Column(
        Integer,
        default=0,
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