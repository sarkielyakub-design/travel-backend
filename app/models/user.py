from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
)
from datetime import datetime

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # ==========================
    # BASIC INFORMATION
    # ==========================

    name = Column(String, nullable=False)

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )

    phone = Column(String)

    profile_photo = Column(String)

    gender = Column(String)

    date_of_birth = Column(String)

    nationality = Column(String)

    # ==========================
    # PASSPORT
    # ==========================

    passport_number = Column(String)

    passport_expiry = Column(String)

    # ==========================
    # ADDRESS
    # ==========================

    country = Column(String)

    state = Column(String)

    city = Column(String)

    address = Column(String)

    # ==========================
    # EMERGENCY CONTACT
    # ==========================

    emergency_contact_name = Column(String)

    emergency_contact_phone = Column(String)

    # ==========================
    # ACCOUNT
    # ==========================

    password = Column(String, nullable=False)

    is_verified = Column(
        Boolean,
        default=False,
    )

    status = Column(
        String,
        default="active",
    )

    # ==========================
    # OTP
    # ==========================

    otp = Column(String)

    otp_expires_at = Column(DateTime)

    # ==========================
    # ROLE
    # ==========================

    role = Column(
        String,
        default="user",
    )

    is_admin = Column(
        Boolean,
        default=False,
    )

    # ==========================
    # TRACKING
    # ==========================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(DateTime)