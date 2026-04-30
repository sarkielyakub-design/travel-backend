from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from app.models.bookings import Booking  # make sure exists
from app.api.deps import get_db, require_admin
from app.models.package import Package
from app.services.payment_service import process_successful_payment

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
    admin=Depends(require_admin),  # 🔐 protect route
):
    image_url = None

    # 📸 HANDLE IMAGE
    if file:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as f:
            f.write(await file.read())

        image_url = f"/{UPLOAD_DIR}/{filename}"

    # 🧱 CREATE PACKAGE
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

        image_url=image_url
    )

    db.add(new_package)
    db.commit()
    db.refresh(new_package)

    return {
        "success": True,
        "message": "Package created",
        "data": new_package
    }


# =========================
# 👑 GET ALL (ADMIN)
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
        "data": packages
    }


# =========================
# 👑 UPDATE PACKAGE
# =========================
@router.put("/packages/{package_id}")
def update_package(
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

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # ✏️ UPDATE FIELDS
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

    db.commit()
    db.refresh(package)

    return {
        "success": True,
        "message": "Package updated",
        "data": package
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
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # 🧹 DELETE IMAGE
    if package.image_url:
        path = package.image_url.lstrip("/")
        if os.path.exists(path):
            os.remove(path)

    db.delete(package)
    db.commit()

    return {
        "success": True,
        "message": "Package deleted"
    }


# =========================
# 📸 UPLOAD IMAGE ONLY
# =========================
@router.post("/packages/{package_id}/upload")
async def upload_image(
    package_id: int,
    file: UploadFile = File(...),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    package.image_url = f"/{UPLOAD_DIR}/{filename}"

    db.commit()
    db.refresh(package)

    return {
        "success": True,
        "image_url": package.image_url
    }
@router.get("/bookings")
def get_admin_bookings(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),  # 🔐 ADD THIS
):
    bookings = db.query(Booking).all()


    return {
        "success": True,
        "total": len(bookings),
        "data": bookings
    }
from sqlalchemy import func



# =========================
# 📊 ADMIN ANALYTICS
# =========================
@router.get("/analytics")
def get_admin_analytics(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0

    paid = db.query(func.count(Booking.id)).filter(
        Booking.status == "paid"
    ).scalar() or 0

    pending = db.query(func.count(Booking.id)).filter(
        Booking.status == "pending"
    ).scalar() or 0

    total_revenue = db.query(func.sum(Package.price))\
        .join(Booking, Booking.package_id == Package.id)\
        .filter(Booking.status == "paid")\
        .scalar() or 0

    conversion_rate = (paid / total_bookings * 100) if total_bookings else 0

    return {
        "success": True,
        "data": {
            "total_bookings": total_bookings,
            "paid": paid,
            "pending": pending,
            "total_revenue": total_revenue,
            "conversion_rate": round(conversion_rate, 2),
        }
    }
# =========================
# 💰 MARK BOOKING AS PAID
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
        raise HTTPException(404, "Booking not found")

    if booking.status == "paid":
        return {
            "success": True,
            "message": "Already marked as paid"
        }

    # ✅ USE CENTRAL LOGIC
    process_successful_payment(booking, db)

    return {
        "success": True,
        "message": "Booking marked as paid and slot updated"
    }
@router.get("/admin/stats")
def get_admin_stats(db: Session = Depends(get_db)):

    total = db.query(Booking).count()
    paid = db.query(Booking).filter(Booking.status == "paid").count()
    pending = db.query(Booking).filter(Booking.status == "pending").count()

    conversion_rate = (paid / total * 100) if total > 0 else 0

    return {
        "total_bookings": total,
        "paid": paid,
        "pending": pending,
        "conversion_rate": round(conversion_rate, 2),
    }