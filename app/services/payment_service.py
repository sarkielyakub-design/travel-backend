from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.bookings import Booking
from app.models.package import Package


def process_successful_payment(booking: Booking, db: Session):
    # 🔒 Lock booking row
    booking = db.query(Booking)\
        .filter(Booking.id == booking.id)\
        .with_for_update()\
        .first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    # 🔁 Idempotency
    if booking.status == "paid":
        return booking

    # 🔒 Lock package row
    package = db.query(Package)\
        .filter(Package.id == booking.package_id)\
        .with_for_update()\
        .first()

    if not package:
        raise HTTPException(404, "Package not found")

    # 🚫 Prevent overbooking
    if package.booked_slots >= package.total_slots:
        raise HTTPException(400, "No available slots")

    # ✅ Update
    booking.status = "paid"
    package.booked_slots += 1

    # 💾 SAVE CHANGES
    db.commit()

    # 🔄 Refresh objects
    db.refresh(booking)
    db.refresh(package)

    return booking