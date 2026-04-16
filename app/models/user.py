from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # 👤 BASIC INFO
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)

    # 🔐 AUTH
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)

    # 🔑 OTP SYSTEM
    otp = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    # 👑 ROLES
    role = Column(String, default="user")  # user / admin
    is_admin = Column(Boolean, default=False)

    # 🕒 TRACKING
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)