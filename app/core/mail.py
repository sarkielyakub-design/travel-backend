from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_booking_email(email, name, booking=None):
    message = MessageSchema(
        subject="Booking Confirmed ✈️",
        recipients=[email],
        body=f"""
        Dear {name},

        Your booking has been successfully confirmed.

        Thank you for choosing M.Y HAMDALA TRAVEL AND TOUR.

        Safe journey ✨
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)