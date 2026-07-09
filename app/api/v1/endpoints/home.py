from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db

from app.models.hero import Hero
from app.models.package import Package
from app.models.news import News
from app.models.gallery import Gallery
from app.models.website_settings import WebsiteSettings

router = APIRouter()


@router.get("/")
def get_home(db: Session = Depends(get_db)):

    try:
        hero = db.query(Hero).first()
        print("✅ Hero OK")
    except Exception as e:
        print("❌ Hero:", e)
        hero = None

    try:
        settings = db.query(WebsiteSettings).first()
        print("✅ Settings OK")
    except Exception as e:
        print("❌ Settings:", e)
        settings = None

    try:
        featured_packages = db.query(Package).limit(6).all()
        print("✅ Packages OK")
    except Exception as e:
        print("❌ Packages:", e)
        featured_packages = []

    try:
        latest_news = db.query(News).limit(3).all()
        print("✅ News OK")
    except Exception as e:
        print("❌ News:", e)
        latest_news = []

    try:
        gallery = db.query(Gallery).limit(8).all()
        print("✅ Gallery OK")
    except Exception as e:
        print("❌ Gallery:", e)
        gallery = []

    return {
        "success": True,
        "data": {
            "hero": hero,
            "settings": settings,
            "featured_packages": featured_packages,
            "latest_news": latest_news,
            "gallery": gallery,
        },
    }