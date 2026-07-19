from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.newsletter import Newsletter
from app.schemas.newsletter import NewsletterCreate

router = APIRouter()
@router.post("/subscribe")
def subscribe(
    data: NewsletterCreate,
    db: Session = Depends(get_db),
):

    existing = db.query(Newsletter).filter(
        Newsletter.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already subscribed.",
        )

    subscriber = Newsletter(
        email=data.email,
    )

    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)

    return {
        "success": True,
        "message": "Subscription successful.",
        "data": subscriber,
    }
@router.get("/")
def get_subscribers(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    subscribers = (
        db.query(Newsletter)
        .order_by(Newsletter.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(subscribers),
        "data": subscribers,
    }
@router.delete("/{subscriber_id}")
def delete_subscriber(
    subscriber_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    subscriber = db.query(Newsletter).filter(
        Newsletter.id == subscriber_id
    ).first()

    if not subscriber:
        raise HTTPException(
            status_code=404,
            detail="Subscriber not found.",
        )

    db.delete(subscriber)
    db.commit()

    return {
        "success": True,
        "message": "Subscriber deleted successfully.",
    }