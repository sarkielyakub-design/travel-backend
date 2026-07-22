import traceback

import cloudinary.uploader

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.gallery import Gallery

router = APIRouter()
@router.post("/")
async def create_gallery(
    title: str = Form(...),
    category: str = Form("General"),
    featured: bool = Form(False),
    active: bool = Form(True),

    file: UploadFile = File(...),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    try:

        result = cloudinary.uploader.upload(
            file.file,
            folder="gallery",
            resource_type="image",
        )

        gallery = Gallery(
            title=title,
            category=category,
            featured=featured,
            active=active,
            image_url=result.get("secure_url"),
            public_id=result.get("public_id"),
        )

        db.add(gallery)
        db.commit()
        db.refresh(gallery)

        return {
            "success": True,
            "message": "Gallery image uploaded successfully.",
            "data": gallery,
        }

    except Exception as e:

        db.rollback()
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
@router.get("/public")
def public_gallery(
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(Gallery.active == True)
        .order_by(Gallery.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "data": gallery,
    }
@router.get("/public/category/{category}")
def gallery_by_category(
    category: str,
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(
            Gallery.category == category,
            Gallery.active == True,
        )
        .order_by(Gallery.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "data": gallery,
    }
@router.get("/public/featured")
def featured_gallery(
    db: Session = Depends(get_db),
):

    gallery = (
        db.query(Gallery)
        .filter(
            Gallery.featured == True,
            Gallery.active == True,
        )
        .order_by(Gallery.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "data": gallery,
    }    
@router.get("/")
def get_gallery(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    gallery = (
        db.query(Gallery)
        .order_by(Gallery.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(gallery),
        "data": gallery,
    }
@router.get("/{gallery_id}")
def get_gallery_by_id(
    gallery_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    gallery = db.query(Gallery).filter(
        Gallery.id == gallery_id
    ).first()

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery image not found",
        )

    return {
        "success": True,
        "data": gallery,
    }
@router.put("/{gallery_id}")
async def update_gallery(
    gallery_id: int,

    title: str = Form(...),
    category: str = Form("General"),
    featured: bool = Form(False),
    active: bool = Form(True),

    file: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    gallery = db.query(Gallery).filter(
        Gallery.id == gallery_id
    ).first()

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery image not found",
        )

    gallery.title = title
    gallery.category = category
    gallery.featured = featured
    gallery.active = active

    if file:

        try:

            if gallery.public_id:
                cloudinary.uploader.destroy(
                    gallery.public_id
                )

            result = cloudinary.uploader.upload(
                file.file,
                folder="gallery",
                resource_type="image",
            )

            gallery.image_url = result.get("secure_url")
            gallery.public_id = result.get("public_id")

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image upload failed: {str(e)}",
            )

    db.commit()
    db.refresh(gallery)

    return {
        "success": True,
        "message": "Gallery updated successfully.",
        "data": gallery,
    }
@router.delete("/{gallery_id}")
def delete_gallery(
    gallery_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    gallery = db.query(Gallery).filter(
        Gallery.id == gallery_id
    ).first()

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery image not found",
        )

    try:
        if gallery.public_id:
            cloudinary.uploader.destroy(
                gallery.public_id
            )
    except Exception as e:
        print(e)

    db.delete(gallery)
    db.commit()

    return {
        "success": True,
        "message": "Gallery deleted successfully.",
    }
