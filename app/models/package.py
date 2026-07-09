from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.session import Base


class Package(Base):
    __tablename__ = "packages"

    # ==========================
    # PRIMARY KEY
    # ==========================
    id = Column(Integer, primary_key=True, index=True)

    # ==========================
    # BASIC INFORMATION
    # ==========================
    title = Column(String, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)

    # ==========================
    # FLIGHT INFORMATION
    # ==========================
    flight_name = Column(String, default="")
    flight_from = Column(String, default="")
    flight_to = Column(String, default="")

    # ==========================
    # TRAVEL DATES
    # ==========================
    departure_date = Column(String, default="")
    return_date = Column(String, default="")

    # ==========================
    # HOTEL INFORMATION
    # ==========================
    hotel_name = Column(String, default="")
    hotel_rating = Column(String, default="3")

    # ==========================
    # PACKAGE CATEGORY
    # ==========================
    category = Column(String, default="standard")

    # ==========================
    # SLOT MANAGEMENT
    # ==========================
    duration_days = Column(Integer, default=0)
    total_slots = Column(Integer, default=0)
    booked_slots = Column(Integer, default=0)

    # ==========================
    # IMAGE (CLOUDINARY)
    # ==========================
    image_url = Column(String, nullable=True)
    public_id = Column(String, nullable=True)

    # ==========================
    # TIMESTAMPS
    # ==========================
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )