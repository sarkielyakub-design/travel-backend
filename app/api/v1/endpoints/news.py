import traceback
from typing import Optional

import cloudinary.uploader
from app.schemas.news import NewsResponse

from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile,
    HTTPException,
)

from sqlalchemy.orm import Session
from sqlalchemy import or_

from slugify import slugify

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.news import News

router = APIRouter()
@router.post("/")
async def create_news(
    title: str = Form(...),
    summary: str = Form(""),
    content: str = Form(...),
    category: str = Form("General"),
    featured: bool = Form(False),
    published: bool = Form(True),

    file: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    try:

        image_url = None
        public_id = None

        slug = slugify(title)

        existing = db.query(News).filter(
            News.slug == slug
        ).first()

        if existing:
            slug = f"{slug}-{existing.id + 1}"

        if file:

            result = cloudinary.uploader.upload(
                file.file,
                folder="news",
                resource_type="image",
            )

            image_url = result.get("secure_url")
            public_id = result.get("public_id")

        news = News(
            title=title,
            slug=slug,
            summary=summary,
            content=content,
            category=category,
            featured=featured,
            published=published,
            image_url=image_url,
            public_id=public_id,
        )

        db.add(news)
        db.commit()
        db.refresh(news)

        return {
            "success": True,
            "message": "News created successfully",
            "data": news,
        }

    except Exception as e:

        db.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )@router.get("/")
def get_news(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    query = db.query(News)

    if search:

        query = query.filter(

            or_(
                News.title.ilike(f"%{search}%"),
                News.category.ilike(f"%{search}%"),
            )

        )

    news = query.order_by(
        News.created_at.desc()
    ).all()

    return {

        "success": True,

        "total": len(news),

        "data": news,

    }@router.get("/{news_id}")
def get_news_by_id(
    news_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    news = db.query(News).filter(
        News.id == news_id
    ).first()

    if not news:

        raise HTTPException(
            404,
            "News not found",
        )

    return {

        "success": True,

        "data": news,

    }
@router.put("/{news_id}")
async def update_news(
    news_id: int,
    title: str = Form(...),
    summary: str = Form(""),
    content: str = Form(...),
    category: str = Form("General"),
    featured: bool = Form(False),
    published: bool = Form(True),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    news = db.query(News).filter(News.id == news_id).first()

    if not news:
        raise HTTPException(404, "News not found")

    news.title = title
    news.slug = slugify(title)
    news.summary = summary
    news.content = content
    news.category = category
    news.featured = featured
    news.published = published

    if file:

        if news.public_id:
            cloudinary.uploader.destroy(news.public_id)

        result = cloudinary.uploader.upload(
            file.file,
            folder="news",
            resource_type="image",
        )

        news.image_url = result["secure_url"]
        news.public_id = result["public_id"]

    db.commit()
    db.refresh(news)

    return {
        "success": True,
        "message": "News updated successfully",
        "data": news,
    }@router.delete("/{news_id}")
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    news = db.query(News).filter(
        News.id == news_id
    ).first()

    if not news:
        raise HTTPException(404, "News not found")

    if news.public_id:
        cloudinary.uploader.destroy(news.public_id)

    db.delete(news)
    db.commit()

    return {
        "success": True,
        "message": "News deleted successfully",
    }@router.get("/public/latest")
def latest_news(db: Session = Depends(get_db)):
    news = (
        db.query(News)
        .filter(News.published == True)
        .order_by(News.created_at.desc())
        .limit(3)
        .all()
    )

    return {
        "success": True,
        "data": news,
    }@router.get("/public")
def public_news(db: Session = Depends(get_db)):
    news = (
        db.query(News)
        .filter(News.published == True)
        .order_by(News.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "data": news,
    }@router.get("/public/{slug}")
def get_news_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    news = db.query(News).filter(
        News.slug == slug,
        News.published == True,
    ).first()

    if not news:
        raise HTTPException(404, "News not found")

    news.views += 1
    db.commit()

    return {
        "success": True,
        "data": news,
    }