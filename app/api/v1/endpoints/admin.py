# =========================
# 🔥 IMPORTS
# =========================

from fastapi import (
    APIRouter,
    Form,
    File,
    UploadFile,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

import os
import uuid

import cloudinary.uploader

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.package import Package
from app.models.bookings import Booking
from app.models.user import User


from app.services.payment_service import (
    process_successful_payment,
)

router = APIRouter()

UPLOAD_DIR = "uploads"


# =========================
# 👑 CREATE PACKAGE
# =========================
@router.post("/packages")
async def create_package(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),

    flight_name: Optional[str] = Form(""),
    flight_from: Optional[str] = Form(""),
    flight_to: Optional[str] = Form(""),

    departure_date: Optional[str] = Form(""),
    return_date: Optional[str] = Form(""),

    hotel_name: Optional[str] = Form(""),
    hotel_rating: Optional[str] = Form("3"),

    category: Optional[str] = Form("standard"),

    duration_days: int = Form(0),
    total_slots: int = Form(0),
    booked_slots: int = Form(0),

    file: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    image_url = None
    public_id = None

    # 🔥 CLOUDINARY UPLOAD
    if file:

        try:

            result = cloudinary.uploader.upload(
                file.file,
                folder="packages",
                resource_type="image",
            )

            image_url = result.get("secure_url")
            public_id = result.get("public_id")

        except Exception as e:
            raise HTTPException(
                500,
                f"Image upload failed: {str(e)}"
            )

    # 🔥 CREATE PACKAGE
    new_package = Package(
        title=title,
        description=description,
        price=price,

        flight_name=flight_name,
        flight_from=flight_from,
        flight_to=flight_to,

        departure_date=departure_date,
        return_date=return_date,

        hotel_name=hotel_name,
        hotel_rating=hotel_rating,

        category=category,

        duration_days=duration_days,
        total_slots=total_slots,
        booked_slots=booked_slots,

        image_url=image_url,
        public_id=public_id,
    )

    db.add(new_package)
    db.commit()
    db.refresh(new_package)

    return {
        "success": True,
        "message": "Package created successfully",
        "data": new_package,
    }


# =========================
# 👑 GET PACKAGES
# =========================
@router.get("/packages")
def get_admin_packages(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    packages = db.query(Package).all()

    return {
        "success": True,
        "total": len(packages),
        "data": packages,
    }


# =========================
# 👑 UPDATE PACKAGE
# =========================
@router.put("/packages/{package_id}")
async def update_package(
    package_id: int,

    title: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),

    flight_name: str = Form(""),
    flight_from: str = Form(""),
    flight_to: str = Form(""),

    departure_date: str = Form(""),
    return_date: str = Form(""),

    hotel_name: str = Form(""),
    hotel_rating: str = Form("3"),

    category: str = Form("standard"),

    duration_days: int = Form(0),
    total_slots: int = Form(0),

    file: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    package = db.query(Package).filter(
        Package.id == package_id
    ).first()

    if not package:
        raise HTTPException(
            404,
            "Package not found"
        )

    # 🔥 UPDATE DATA
    package.title = title
    package.description = description
    package.price = price

    package.flight_name = flight_name
    package.flight_from = flight_from
    package.flight_to = flight_to

    package.departure_date = departure_date
    package.return_date = return_date

    package.hotel_name = hotel_name
    package.hotel_rating = hotel_rating

    package.category = category

    package.duration_days = duration_days
    package.total_slots = total_slots

    # 🔥 UPDATE IMAGE
    if file:

        try:

            if package.public_id:
                cloudinary.uploader.destroy(
                    package.public_id
                )

            result = cloudinary.uploader.upload(
                file.file,
                folder="packages",
            )

            package.image_url = result.get(
                "secure_url"
            )

            package.public_id = result.get(
                "public_id"
            )

        except Exception as e:
            raise HTTPException(
                500,
                f"Image update failed: {str(e)}"
            )

    db.commit()
    db.refresh(package)

    return {
        "success": True,
        "message": "Package updated",
        "data": package,
    }


# =========================
# 👑 DELETE PACKAGE
# =========================
@router.delete("/packages/{package_id}")
def delete_package(
    package_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    package = db.query(Package).filter(
        Package.id == package_id
    ).first()

    if not package:
        raise HTTPException(
            404,
            "Package not found"
        )

    # 🔥 DELETE IMAGE
    try:

        if package.public_id:
            cloudinary.uploader.destroy(
                package.public_id
            )

    except Exception as e:
        print(e)

    db.delete(package)
    db.commit()

    return {
        "success": True,
        "message": "Package deleted",
    }


# =========================
# 📘 GET BOOKINGS
# =========================
@router.get("/bookings")
def get_admin_bookings(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    bookings = (
        db.query(Booking)
        .order_by(Booking.id.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(bookings),
        "data": bookings,
    }


# =========================
# 👥 GET USERS
# =========================
@router.get("/users")
def get_admin_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    users = (
        db.query(User)
        .order_by(User.id.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(users),
        "data": users,
    }


# =========================
# 💳 GET PAYMENTS
# =========================

# =========================
# 📊 ADMIN ANALYTICS
# =========================
# =========================
# 📊 ADMIN ANALYTICS
# =========================
@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    # BOOKINGS
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    paid = (
        db.query(func.count(Booking.id))
        .filter(Booking.status == "paid")
        .scalar()
    ) or 0

    pending = (
        db.query(func.count(Booking.id))
        .filter(Booking.status != "paid")
        .scalar()
    ) or 0

    # USERS
    total_users = db.query(func.count(User.id)).scalar() or 0

    # PACKAGES
    total_packages = db.query(func.count(Package.id)).scalar() or 0

    # PAYMENTS (Paid bookings)
    total_payments = paid

    # REVENUE
    total_revenue = (
        db.query(func.sum(Package.price))
        .join(
            Booking,
            Booking.package_id == Package.id
        )
        .filter(
            Booking.status == "paid"
        )
        .scalar()
    ) or 0

    # CONVERSION
    conversion_rate = (
        round((paid / total_bookings) * 100, 2)
        if total_bookings > 0
        else 0
    )

    # RECENT BOOKINGS
    latest_bookings = (
        db.query(Booking)
        .order_by(Booking.id.desc())
        .limit(5)
        .all()
    )

    return {
        "success": True,
        "data": {
            "total_bookings": total_bookings,
            "paid": paid,
            "pending": pending,
            "total_users": total_users,
            "total_packages": total_packages,
            "total_payments": total_payments,
            "revenue": float(total_revenue),
            "conversion_rate": conversion_rate,
            "recent_activity": latest_bookings,
        },
    }


# =========================
# 💰 MARK BOOKING PAID
# =========================
@router.put("/bookings/{booking_id}/pay")
def mark_booking_paid(
    booking_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    booking = db.query(Booking).filter(
        Booking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            404,
            "Booking not found"
        )

    if booking.status == "paid":
        return {
            "success": True,
            "message": "Already paid",
        }

    # 🔥 PROCESS PAYMENT
    process_successful_payment(
        booking,
        db
    )

    return {
        "success": True,
        "message": "Booking marked as paid",
    }


# =========================
# 📈 LIVE STATS
# =========================
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    total_bookings = db.query(Booking).count()

    paid = (
        db.query(Booking)
        .filter(Booking.status == "paid")
        .count()
    )

    pending = (
        db.query(Booking)
        .filter(Booking.status != "paid")
        .count()
    )

    total_users = db.query(User).count()

    total_packages = db.query(Package).count()

    total_payments = paid

    conversion_rate = (
        round((paid / total_bookings) * 100, 2)
        if total_bookings > 0
        else 0
    )

    return {
        "success": True,
        "data": {
            "total_bookings": total_bookings,
            "paid": paid,
            "pending": pending,
            "total_users": total_users,
            "total_packages": total_packages,
            "total_payments": total_payments,
            "conversion_rate": conversion_rate,
        },
    }