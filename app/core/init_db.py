from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def init_admin():
    db: Session = SessionLocal()

    admin = db.query(User).filter(User.email == "admin@myhamdala.com").first()

    if not admin:
        admin = User(
            name="Super Admin",
            email="admin@myhamdala.com",
            password=hash_password("admin123"),
            role="admin"
            is_verified=True
        )
        db.add(admin)
        db.commit()
        print("🔥 Admin created: admin@myhamdala.com / admin123")

    db.close()