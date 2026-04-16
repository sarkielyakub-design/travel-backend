# app/models/chat.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.session import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    message = Column(Text)
    reply = Column(Text, nullable=True)
    status = Column(String, default="open")  # open / closed
    created_at = Column(DateTime, default=datetime.utcnow)