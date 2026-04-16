import requests
from app.core.config import PAYSTACK_SECRET_KEY

BASE_URL = "https://api.paystack.co"


def initialize_payment(email: str, amount: int):
    url = f"{BASE_URL}/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": email,
        "amount": amount * 100,  # Paystack uses kobo
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()