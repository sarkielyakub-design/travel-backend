from pydantic import BaseModel, Field
from typing import Optional


class PackageCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: str
    price: int = Field(..., gt=0)


class PackageUpdate(BaseModel):
    title: str
    description: str
    price: int


class PackageOut(BaseModel):
    id: int
    title: str
    description: str
    price: int
    image_url: Optional[str] = None  # ✅ FIXED

    class Config:
        orm_mode = True  # ✅ for SQLAlchemy (Python 3.9)