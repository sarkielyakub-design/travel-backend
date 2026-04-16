from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# PASSWORD
# =========================
import hashlib

def hash_password(password: str):
    # 🔥 hash first (no length limit)
    hashed = hashlib.sha256(password.encode()).hexdigest()

    return pwd_context.hash(hashed)


def verify_password(password: str, hashed_password: str):
    hashed = hashlib.sha256(password.encode()).hexdigest()

    return pwd_context.verify(hashed, hashed_password)

# =========================
# TOKENS
# =========================
def create_access_token(data: dict) -> str:
    now = datetime.utcnow()
    return jwt.encode({
        "sub": data["sub"],
        "type": "access",
        "iat": now,
        "exp": now + timedelta(hours=2)
    }, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    now = datetime.utcnow()
    return jwt.encode({
        "sub": data["sub"],
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=7)
    }, SECRET_KEY, algorithm=ALGORITHM)


# =========================
# ✅ THIS IS YOUR MISSING FUNCTION
# =========================
def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None