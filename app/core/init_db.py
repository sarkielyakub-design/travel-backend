from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def init_admin():
    db: Session = SessionLocal()

    admin = db.query(User).filter(User.email == "myhamdala2020@gmail.com").first()

    if not admin:
        admin = User(
            name="Super Admin",
            email="myhamdala2020@gmail.com",
            password=hash_password("Danmaiwaina2020"),
            role="admin",
            is_verified=True  # ✅ FIXED
        )
        db.add(admin)
        print("🔥 Admin created:myhamdala2020@gmail.com / Danmaiwaina2020")

    else:
        # 🔥 VERY IMPORTANT (fix existing admin)
        admin.is_verified = True
        print("✅ Admin already exists → forced verified")

    db.commit()
    db.close()