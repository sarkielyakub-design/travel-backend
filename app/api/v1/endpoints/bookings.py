from fastapi import APIRouter, Depends, HTTPException, Body, status, Request
from sqlalchemy.orm import Session
import requests, uuid, hmac, hashlib, json, asyncio, logging, os
from datetime import datetime
from app.api.deps import get_current_user, get_db
from app.models.bookings import Booking
from app.models.package import Package
from app.schemas.bookings import BookingCreate
from app.services.payment import initialize_payment
from app.core.mail import send_booking_email
from app.api.deps import require_admin
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Bookings"])


# =========================
# 🧾 CREATE BOOKING + PAYMENT (CLEAN)
# =========================from datetime import datetime
import uuid

@router.post("/create-and-pay", status_code=status.HTTP_201_CREATED)
def create_and_pay(
    package_id: int,
    data: BookingCreate = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        # 📦 GET PACKAGE
        package = db.query(Package).filter(Package.id == package_id).first()

        if not package:
            raise HTTPException(404, "Package not found")

        if package.booked_slots >= package.total_slots:
            raise HTTPException(400, "No available slots")

        # 🔁 CHECK EXISTING PENDING
        existing = db.query(Booking).filter(
            Booking.user_id == user.id,
            Booking.package_id == package.id,
            Booking.status == "pending"
        ).first()

        if existing and existing.payment_url:
            return {
                "message": "Pending booking already exists",
                "booking_id": existing.id,
                "authorization_url": existing.payment_url,
                "reference": existing.payment_reference,
            }

        # 🔑 GENERATE REFERENCE
        reference = f"BOOK-{uuid.uuid4().hex}"

        # ✅ CONVERT DATES (FIX SQLITE ERROR)
        try:
            date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d").date()
            passport_issue = datetime.strptime(data.passport_issue, "%Y-%m-%d").date()
            passport_expiry = datetime.strptime(data.passport_expiry, "%Y-%m-%d").date()
        except Exception:
            raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

        # 🧾 CREATE BOOKING
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
            date_of_birth=date_of_birth,       # ✅ FIXED
            passport_issue=passport_issue,     # ✅ FIXED
            passport_expiry=passport_expiry,   # ✅ FIXED
            status="pending",
            payment_reference=reference
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        # 💳 INIT PAYSTACK
        payment = initialize_payment(
            email=data.email,
            amount=500000,# kobo
            reference=reference,
            
        )

        print("🔥 PAYSTACK:", payment)

        # ❌ HANDLE PAYSTACK FAILURE
        if not payment or payment.get("status") is False:
            db.delete(booking)
            db.commit()
            raise HTTPException(
                400,
                payment.get("message", "Payment initialization failed")
            )

        # ✅ SAVE PAYMENT LINK
        booking.payment_url = payment.get("authorization_url")
        db.commit()

        return {
            "message": "Booking created successfully",
            "booking_id": booking.id,
            "authorization_url": booking.payment_url,
            "reference": reference,
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        print("🔥 CREATE BOOKING ERROR:", str(e))
        raise HTTPException(500, "Internal server error")
# =========================
# 👤 GET USER BOOKINGS
# =========================
@router.get("/")
def get_my_bookings(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Booking).filter(
        Booking.user_id == user.id
    ).order_by(Booking.id.desc()).all()


# =========================
# 🔍 VERIFY PAYMENT
# =========================
@router.get("/verify/{reference}")
def verify_payment(reference: str, db: Session = Depends(get_db)):
    PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}"
    }

    res = requests.get(url, headers=headers).json()

    if not res.get("status"):
        raise HTTPException(400, "Payment verification failed")

    data = res["data"]

    if data["status"] != "success":
        raise HTTPException(400, "Payment not successful")

    booking = db.query(Booking).filter(
        Booking.payment_reference == reference
    ).first()

    if not booking:
        raise HTTPException(404, "Booking not found")

    if booking.status != "paid":
        booking.status = "paid"

        package = db.query(Package).filter(
            Package.id == booking.package_id
        ).first()

        if package:
            package.booked_slots += 1

        db.commit()

        # 📧 EMAIL
        asyncio.create_task(
            send_booking_email(
                booking.email,
                booking.first_name,
                package.title if package else "Package"
            )
        )

    return {"success": True}


# =========================
# 🔥 PAYSTACK WEBHOOK
# =========================
@router.post("/webhook")
async def paystack_webhook(request: Request, db: Session = Depends(get_db)):
    PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")

    body = await request.body()
    signature = request.headers.get("x-paystack-signature")

    # 🔐 VERIFY SIGNATURE
    computed_hash = hmac.new(
        PAYSTACK_SECRET.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if computed_hash != signature:
        raise HTTPException(400, "Invalid signature")

    payload = json.loads(body)

    if payload.get("event") != "charge.success":
        return {"status": "ignored"}

    data = payload["data"]
    reference = data.get("reference")

    booking = db.query(Booking).filter(
        Booking.payment_reference == reference
    ).first()

    if not booking:
        return {"status": "booking not found"}

    if booking.status != "paid":
        booking.status = "paid"

        package = db.query(Package).filter(
            Package.id == booking.package_id
        ).first()

        if package:
            package.booked_slots += 1

        db.commit()

        # =========================
        # 📧 EMAIL (SAFE THREAD)
        # =========================
        try:
            threading.Thread(
                target=lambda: asyncio.run(
                    send_booking_email(
                        booking.email,
                        booking.first_name
                    )
                )
            ).start()
        except Exception as e:
            print("Email error:", e)

        # =========================
        # 📲 WHATSAPP (TWILIO)
        # =========================
        try:
            account_sid = os.getenv("TWILIO_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")

            client = Client(account_sid, auth_token)

            message = f"""
🕋 M.Y HAMDALA TRAVEL AND TOUR

Hello {booking.first_name},

✅ Your booking is CONFIRMED!

📦 Package: {package.title if package else "Package"}
💰 Amount: ₦{package.price if package else ""}
📅 Departure: {package.departure_date if package else ""}

We will contact you shortly.

Thank you 🙏
"""

            client.messages.create(
                body=message,
                from_="whatsapp:+14155238886",  # Twilio sandbox
                to=f"whatsapp:{booking.phone}"
            )

        except Exception as e:
            print("WhatsApp error:", e)

    return {"status": "success"}
