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
@router.get("/")
def get_hero(
    db: Session = Depends(get_db),
):

    hero = db.query(Hero).first()

    return {
        "success": True,
        "data": hero,
    }
@router.put("/")
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
    print("TITLE =", title)

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

    if file is not None:

        if hero.public_id:
            cloudinary.uploader.destroy(hero.public_id)

        result = cloudinary.uploader.upload(
            file.file,
            folder="hero",
            resource_type="image",
        )

        hero.image_url = result["secure_url"]
        hero.public_id = result["public_id"]

    db.commit()
    db.refresh(hero)

    return {
        "success": True,
        "message": "Hero updated successfully.",
        "data": hero,
    }