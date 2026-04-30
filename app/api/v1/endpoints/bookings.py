from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from sqlalchemy.orm import Session
import requests, uuid, hmac, hashlib, json, os, logging
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.models.bookings import Booking
from app.models.package import Package
from app.schemas.bookings import BookingCreate
from app.core.mail import send_booking_email

router = APIRouter(tags=["Bookings"])
logger = logging.getLogger(__name__)

PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_URL = "https://api.paystack.co/transaction/initialize"


# =========================
# 🧾 CREATE BOOKING + PAYMENT
# =========================
@router.post("/create-and-pay", status_code=201)
def create_and_pay(
    package_id: int,
    data: BookingCreate = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(404, "Package not found")

        if package.booked_slots >= package.total_slots:
            raise HTTPException(400, "No available slots")

        # 🔒 Prevent duplicate pending (FIXED)
        existing = db.query(Booking).filter(
            Booking.user_id == user.id,
            Booking.package_id == package.id,
            Booking.status == "pending"
        ).first()

        if existing:
            if existing.expires_at and existing.expires_at < datetime.utcnow():
                existing.status = "cancelled"
                db.commit()
            else:
                return {
                    "message": "Pending booking already exists",
                    "booking_id": existing.id,
                    "authorization_url": existing.payment_url,
                    "reference": existing.payment_reference,
                }

        reference = f"BOOK-{uuid.uuid4().hex}"

        # 📅 Validate dates
        try:
            dob = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
            issue = datetime.strptime(data.passport_issue, "%Y-%m-%d").date()
            expiry = datetime.strptime(data.passport_expiry, "%Y-%m-%d").date()
        except:
            raise HTTPException(400, "Invalid date format")

        amount_kobo = int(package.price * 100)

        booking = Booking(
            user_id=user.id,
            package_id=package.id,
            surname=data.surname,
            first_name=data.first_name,
            given_names=data.given_names,
            nationality=data.nationality,
            email=data.email,
            phone=data.phone,
            passport_number=data.passport_number,
            place_of_birth=data.place_of_birth,
            date_of_birth=dob,
            passport_issue=issue,
            passport_expiry=expiry,
            status="pending",
            payment_reference=reference,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        # 💳 INIT PAYSTACK
        payload = {
            "email": booking.email,
            "amount": amount_kobo,
            "reference": reference,
            "callback_url": f"{os.getenv('FRONTEND_URL')}/payment-success",
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET}",
            "Content-Type": "application/json",
        }

        response = requests.post(PAYSTACK_URL, json=payload, headers=headers).json()

        if not response.get("status"):
            db.delete(booking)
            db.commit()
            raise HTTPException(400, response.get("message"))

        booking.payment_url = response["data"]["authorization_url"]
        db.commit()

        return {
            "booking_id": booking.id,
            "authorization_url": booking.payment_url,
            "reference": reference,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"CREATE ERROR: {e}")
        raise HTTPException(500, "Internal error")

# =========================
# 👤 USER BOOKINGS
# =========================
@router.get("/")
def get_my_bookings(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Booking)\
        .filter(Booking.user_id == user.id)\
        .order_by(Booking.id.desc())\
        .all()


# =========================
# 🔍 VERIFY PAYMENT
# =========================
@router.get("/verify/{reference}")
def verify_payment(reference: str, db: Session = Depends(get_db)):

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}

    res = requests.get(url, headers=headers).json()

    if not res.get("status"):
        raise HTTPException(400, "Verification failed")

    data = res["data"]

    booking = db.query(Booking)\
        .filter(Booking.payment_reference == reference)\
        .first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    # ⛔ EXPIRED CHECK
    if booking.expires_at and booking.expires_at < datetime.utcnow():
        booking.status = "cancelled"
        db.commit()
        raise HTTPException(400, "Booking expired")

    if booking.status == "paid":
        return {"success": True}

    if data["status"] != "success":
        raise HTTPException(400, "Payment failed")

    # ✅ USE SAFE FUNCTION
    process_successful_payment(booking, db)

    send_booking_email(
        booking.email,
        booking.first_name,
        booking.package.title if booking.package else "Package"
    )

    return {"success": True}

# =========================
# 🔥 WEBHOOK (FINAL CLEAN)
# =========================
from app.services.payment_service import process_successful_payment

@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.body()
        signature = request.headers.get("x-paystack-signature")

        if not signature:
            raise HTTPException(400, "Missing signature")

        # 🔐 VERIFY SIGNATURE
        computed_hash = hmac.new(
            PAYSTACK_SECRET.encode(),
            body,
            hashlib.sha512
        ).hexdigest()

        if computed_hash != signature:
            raise HTTPException(400, "Invalid signature")

        payload = json.loads(body)

        # ✅ ONLY HANDLE SUCCESS
        if payload.get("event") != "charge.success":
            return {"status": "ignored"}

        data = payload.get("data", {})
        reference = data.get("reference")

        if not reference:
            return {"status": "no reference"}

        # 🔒 LOCK BOOKING
        booking = (
            db.query(Booking)
            .filter(Booking.payment_reference == reference)
            .with_for_update()
            .first()
        )

        if not booking:
            return {"status": "booking not found"}

        # ⛔ EXPIRED CHECK
        if booking.expires_at and booking.expires_at < datetime.utcnow():
            booking.status = "cancelled"
            db.commit()
            return {"status": "expired"}

        # 🔁 IDEMPOTENCY (VERY IMPORTANT)
        if booking.status == "paid":
            return {"status": "already processed"}

        # 🔒 LOCK PACKAGE
        package = (
            db.query(Package)
            .filter(Package.id == booking.package_id)
            .with_for_update()
            .first()
        )

        if not package:
            return {"status": "package not found"}

        # 🚫 PREVENT OVERBOOKING
        if package.booked_slots >= package.total_slots:
            booking.status = "failed"
            db.commit()
            return {"status": "no slots"}

        # ✅ UPDATE STATE
        booking.status = "paid"
        package.booked_slots += 1

        db.commit()

        # 📧 EMAIL (NON-CRITICAL)
        try:
            send_booking_email(
                booking.email,
                booking.first_name,
                package.title
            )
        except Exception as e:
            logger.warning(f"Email failed: {e}")

        logger.info(f"✅ Payment success processed: {reference}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"🔥 WEBHOOK ERROR: {str(e)}")
        raise HTTPException(500, "Webhook failed")