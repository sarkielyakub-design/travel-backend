from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.package import Package

router = APIRouter()

@router.get("packages")
def get_packages(db: Session = Depends(get_db)):
    packages = db.query(Package).all()

    return {
        "success": True,
        "count": len(packages),
        "data": packages
    }

@router.get("/{package_id}")
def get_package(package_id: int, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.id == package_id).first()

    if not package:
        raise HTTPException(404, "Not found")

    return package