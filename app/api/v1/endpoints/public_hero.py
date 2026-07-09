from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.hero import Hero

router = APIRouter()


@router.get("/")
def get_hero(db: Session = Depends(get_db)):
    hero = db.query(Hero).first()

    return {
        "success": True,
        "data": hero,
    }