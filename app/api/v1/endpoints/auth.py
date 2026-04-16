from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import LoginSchema
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


import random

from app.services.email import send_email
import random
from datetime import datetime, timedelta

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    otp = str(random.randint(100000, 999999))

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        otp=otp,
        otp_expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(new_user)
    db.commit()

    # ✅ SEND EMAIL
    send_email(
        to_email=user.email,
        subject="Verify your account",
        body=f"Your OTP is: {otp}\nThis expires in 5 minutes."
    )

    return {"message": "OTP sent to email"}
@router.post("/verify")
def verify(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or user.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    user.is_verified = True
    user.otp = None

    db.commit()

    return {"message": "Verified"}
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
@router.post("/reset-password")
def reset(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user or user.otp != otp:
        raise HTTPException(400, "Invalid OTP")

    user.password = hash_password(new_password)
    user.otp = None

    db.commit()

    return {"message": "Password updated"}

@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({
        "sub": user.email,
        "role": user.role,   # ✅ IMPORTANT
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
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_token
from app.models.token_blacklist import TokenBlacklist

@router.post("/logout")
def logout(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    blacklisted = TokenBlacklist(token=token)
    db.add(blacklisted)
    db.commit()

    return {"message": "Logged out successfully"}
@router.post("/refresh")
def refresh(token: str = Depends(get_token)):
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = create_access_token({"sub": payload.get("sub")})

    return {"access_token": new_access}