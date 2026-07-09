from datetime import datetime
from pydantic import BaseModel


class GalleryBase(BaseModel):
    title: str
    category: str = "General"
    featured: bool = False
    active: bool = True


class GalleryCreate(GalleryBase):
    pass


class GalleryUpdate(GalleryBase):
    pass


class GalleryResponse(GalleryBase):
    id: int
    image_url: str
    public_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True