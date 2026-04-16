import requests
from app.core.config import settings


def initialize_payment(email: str, amount: int, reference: str):
    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": int(amount * 100),  # 🔥 Paystack uses kobo
        "reference": reference,
        "callback_url": "http://localhost:3000/payment-success"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    print("🔥 PAYSTACK:", data)

    if not data.get("status"):
        raise Exception(data.get("message"))

    return data["data"]