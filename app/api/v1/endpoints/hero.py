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

from app.models.hero import Hero

router = APIRouter()


# =========================================================
# PUBLIC HERO
# =========================================================
@router.get("/")
def get_hero(
    db: Session = Depends(get_db),
):
    hero = db.query(Hero).first()

    if hero is None:
        raise HTTPException(
            status_code=404,
            detail="Hero section not found."
        )

    return {
        "success": True,
        "data": hero,
    }


# =========================================================
# UPDATE HERO
# =========================================================
@router.put("/")
async def update_hero(
    title: str = Form(...),
    subtitle: str = Form(""),

    primary_button_text: str = Form(...),
    primary_button_link: str = Form(...),

    secondary_button_text: str = Form(...),
    secondary_button_link: str = Form(...),

    booking_url: str = Form(...),

    file: UploadFile = File(None),

    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    try:

        hero = db.query(Hero).first()

        if hero is None:
            hero = Hero()
            db.add(hero)

        hero.title = title
        hero.subtitle = subtitle

        hero.primary_button_text = primary_button_text
        hero.primary_button_link = primary_button_link

        hero.secondary_button_text = secondary_button_text
        hero.secondary_button_link = secondary_button_link

        hero.booking_url = booking_url

        # Upload new image if provided
        if file is not None:

            # Delete old image
            if hero.public_id:
                try:
                    cloudinary.uploader.destroy(hero.public_id)
                except Exception:
                    pass

            result = cloudinary.uploader.upload(
                file.file,
                folder="hero",
                resource_type="image",
            )

            hero.image_url = result.get("secure_url")
            hero.public_id = result.get("public_id")

        db.commit()
        db.refresh(hero)

        return {
            "success": True,
            "message": "Hero updated successfully.",
            "data": hero,
        }

    except Exception as e:

        db.rollback()

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )