from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.core.security import decode_token


# =========================
# 🗄️ DATABASE DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 🔑 EXTRACT TOKEN
# =========================
def get_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format. Use Bearer <token>"
        )

    return authorization.split(" ")[1]


# =========================
# 👤 GET CURRENT USER
# =========================
def get_current_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
):
    # 🔒 CHECK BLACKLIST
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    # 🔐 DECODE TOKEN
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # 📧 GET USER EMAIL
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identity"
        )

    # 👤 FETCH USER
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =========================
# 🔐 ADMIN ONLY (IMPROVED)
# =========================
def require_admin(
    current_user: User = Depends(get_current_user)
):
    # ✅ SAFE CHECK (prevents crash if role missing)
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admins only"
        )

    return current_user


# =========================
# 🔐 MULTI-ROLE SYSTEM (PRO)
# =========================
def require_roles(*roles: str):
    def checker(current_user: User = Depends(get_current_user)):
        if getattr(current_user, "role", None) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires one of {roles}"
            )
        return current_user
    return checker