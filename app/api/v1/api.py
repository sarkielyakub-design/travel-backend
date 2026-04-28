from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    packages,
    bookings,
    admin,
)

api_router = APIRouter()

# 🔐 AUTH
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])

# 👤 USERS
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# 📦 PACKAGES
api_router.include_router(packages.router, prefix="/packages", tags=["Packages"])

# 📘 BOOKINGS
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

# 🛠️ ADMIN
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])