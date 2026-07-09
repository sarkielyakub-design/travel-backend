from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewsBase(BaseModel):
    title: str
    summary: Optional[str] = ""
    content: str
    category: Optional[str] = "General"
    featured: bool = False
    published: bool = True


class NewsCreate(NewsBase):
    pass


class NewsUpdate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    slug: str
    image_url: Optional[str] = None
    public_id: Optional[str] = None
    views: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True