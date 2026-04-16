from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db   # ✅ FIXED HERE
from app.models.chat import Chat

router = APIRouter(prefix="/chat", tags=["Chat"])

# 📩 USER SEND MESSAGE
@router.post("/")
def send_message(message: str, db: Session = Depends(get_db)):
    chat = Chat(message=message)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


# 📥 GET ALL (ADMIN)
@router.get("/")
def get_chats(db: Session = Depends(get_db)):
    return db.query(Chat).order_by(Chat.id.desc()).all()


# 💬 ADMIN REPLY
@router.post("/{chat_id}/reply")
def reply(chat_id: int, reply: str, db: Session = Depends(get_db)):
    chat = db.query(Chat).get(chat_id)
    chat.reply = reply
    chat.status = "closed"
    db.commit()
    return {"message": "Replied"}