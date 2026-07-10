from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_admin,
)

from app.models.user import User

router = APIRouter()


@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):

    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(users),
        "data": users,
    }