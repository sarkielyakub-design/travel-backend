from sqlalchemy.orm import Session
from datetime import datetime
from app.models.bookings import Booking


def expire_bookings(db: Session):
    now = datetime.utcnow()

    expired = db.query(Booking).filter(
        Booking.status == "pending",
        Booking.expires_at < now
    ).all()

    for b in expired:
        b.status = "cancelled"

    db.commit()