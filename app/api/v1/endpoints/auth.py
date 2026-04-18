from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.schemas.user import UserCreate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)

from app.services.email import send_email
from app.api.deps import get_token
from app.models.token_blacklist import TokenBlacklist

router = APIRouter()


# =========================
# DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# REGISTER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        is_verified=True  # ✅ AUTO VERIFY
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Account created successfully",
        "user_id": new_user.id
    }

# =========================
# VERIFY OTP
# =========================
@router.post("/verify")
def verify(email: str, otp: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user or user.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    user.is_verified = True
    user.otp = None

    db.commit()

    return {"message": "Account verified"}


# =========================
# FORGOT PASSWORD
# =========================
@router.post("/forgot-password")
def forgot(email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(404, "User not found")

    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    send_email(
        to_email=email,
        subject="Reset your password",
        body=f"Your reset OTP is: {otp}"
    )

    return {"message": "OTP sent"}


# =========================
# RESET PASSWORD
# =========================
@router.post("/reset-password")
def reset(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user or user.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    user.password = hash_password(new_password)  # ✅ SAFE
    user.otp = None

    db.commit()

    return {"message": "Password updated"}


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    if not user.is_verified:
        raise HTTPException(403, "Account not verified")

    token = create_access_token({
        "sub": user.email,
        "role": user.role,
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.role == "admin"
        }
    }


# =========================
# LOGOUT
# =========================
@router.post("/logout")
def logout(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):

    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

    return {"message": "Logged out successfully"}


# =========================
# REFRESH TOKEN
# =========================
@router.post("/refresh")
def refresh(token: str = Depends(get_token)):

    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")

    new_access = create_access_token({"sub": payload.get("sub")})

    return {"access_token": new_access}