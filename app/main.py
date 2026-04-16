from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine
from app.core.init_db import init_admin


# =========================
# 🧠 LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =========================
# 📁 UPLOAD FOLDER
# =========================
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================
# 🚀 CREATE APP
# =========================
app = FastAPI(
    title="M.Y HAMDALA TRAVEL API",
    version="2.0.0",
    description="🚀 Premium Travel Booking System API",
    swagger_ui_parameters={"persistAuthorization": True},
)


# =========================
# 🌐 CORS (FIXED 🔥)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔥 allow all during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# 📁 STATIC FILES (FIXED)
# =========================
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# =========================
# 🔌 STARTUP EVENT
# =========================
@app.on_event("startup")
def startup():
    try:
        logger.info("🚀 Starting M.Y HAMDALA API...")

        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database ready")

        init_admin()
        logger.info("✅ Admin initialized")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise e


# =========================
# 🔗 ROUTES
# =========================
app.include_router(api_router, prefix="/api/v1")


# =========================
# 🏠 ROOT
# =========================
@app.get("/")
def root():
    return {
        "message": "🚀 M.Y HAMDALA API running",
        "version": "2.0.0",
        "status": "healthy"
    }


# =========================
# ❤️ HEALTH
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# 🔐 CUSTOM SWAGGER JWT
# =========================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="M.Y HAMDALA API",
        version="2.0.0",
        description="Travel Booking System",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi