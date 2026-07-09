import cloudinary.uploader

from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.website_settings import WebsiteSettings

router = APIRouter()
@router.get("/")
def get_settings(
    db: Session = Depends(get_db),
):

    settings = db.query(
        WebsiteSettings
    ).first()

    return {
        "success": True,
        "data": settings,
    }
@router.put("/")
async def update_settings(
    company_name: str = Form(...),
    company_email: str = Form(""),
    phone_one: str = Form(""),
    phone_two: str = Form(""),
    address: str = Form(""),
    business_hours: str = Form(""),

    booking_url: str = Form(""),
    whatsapp: str = Form(""),

    facebook: str = Form(""),
    instagram: str = Form(""),
    linkedin: str = Form(""),
    twitter: str = Form(""),
    youtube: str = Form(""),
    tiktok: str = Form(""),

    google_maps: str = Form(""),

    seo_title: str = Form(""),
    seo_description: str = Form(""),

    footer_text: str = Form(""),

    logo: UploadFile = File(None),
    favicon: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):    settings = db.query(
        WebsiteSettings
    ).first()