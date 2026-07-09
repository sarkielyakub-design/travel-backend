from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)

from datetime import datetime

from app.db.session import Base


class Newsletter(Base):
    __tablename__ = "newsletter"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
    )

    active = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )