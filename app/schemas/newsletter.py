from datetime import datetime
from pydantic import BaseModel, EmailStr


class NewsletterCreate(BaseModel):
    email: EmailStr


class NewsletterResponse(BaseModel):
    id: int
    email: EmailStr
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True