from fastapi import APIRouter
from app.api.v1.endpoints import newsletter
from app.api.v1.endpoints import hero
from app.api.v1.endpoints import website_settings
from app.api.v1.endpoints import home
from app.api.v1.endpoints import (
    auth,
    users,
    packages,
    bookings,
    admin,
    news,
    gallery,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

api_router.include_router(users.router, prefix="/users", tags=["Users"])

api_router.include_router(packages.router, prefix="/packages", tags=["Packages"])

api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])

api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

api_router.include_router(
    news.router,
    prefix="/admin/news",
    tags=["Admin News"],
)

api_router.include_router(
    gallery.router,
    prefix="/admin/gallery",
    tags=["Admin Gallery"],
)

api_router.include_router(
    newsletter.router,
    prefix="/admin/newsletter",
    tags=["Admin Newsletter"],
)

api_router.include_router(
    hero.router,
    prefix="/admin/hero",
    tags=["Admin Hero"],
)

api_router.include_router(
    website_settings.router,
    prefix="/admin/settings",
    tags=["Admin Website Settings"],
)
from app.api.v1.endpoints import public_hero

api_router.include_router(
    public_hero.router,
    prefix="/hero",
    tags=["Hero"],
)
api_router.include_router(
    home.router,
    prefix="/home",
    tags=["Home"],
)