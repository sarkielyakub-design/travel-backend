from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.base import Base


class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)

    # ✈️ FLIGHT
    flight_name = Column(String, default="")
    flight_from = Column(String, default="")
    flight_to = Column(String, default="")

    # 📅 DATE
    departure_date = Column(String, default="")
    return_date = Column(String, default="")

    # 🏨 HOTEL
    hotel_name = Column(String, default="")
    hotel_rating = Column(String, default="3")

    # 🏷 CATEGORY
    category = Column(String, default="standard")

    # 📊 SLOTS
    duration_days = Column(Integer, default=0)
    total_slots = Column(Integer, default=0)
    booked_slots = Column(Integer, default=0)

    # 🖼 IMAGE
    image_url = Column(String, nullable=True)

    # 🔥 IMPORTANT (ADD THIS)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    public_id = Column(String, nullable=True)
    
