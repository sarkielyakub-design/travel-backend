from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    # 🔗 RELATIONSHIPS
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)

    # 🛂 PERSONAL INFO
    surname = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    given_names = Column(String, nullable=True)
    nationality = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # 🧾 PASSPORT INFO
    passport_number = Column(String, nullable=False)
    place_of_birth = Column(String, nullable=False)

    # 📅 DATE FIELDS
    date_of_birth = Column(Date, nullable=False)
    passport_issue = Column(Date, nullable=False)
    passport_expiry = Column(Date, nullable=False)

    # 💰 PAYMENT STATUS
    status = Column(String, default="pending", index=True)

    # 🔥 PAYMENT DATA
    payment_reference = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        default=lambda: f"BOOK-{uuid.uuid4().hex}"
    )

    payment_url = Column(String, nullable=True)

    # ✅ NEW: EXPIRATION (FIXED PROPERLY)
    expires_at = Column(DateTime, nullable=True, index=True)

    # 🕒 TIMESTAMPS
    created_at = Column(DateTime(timezone=True), server_default=func.now())