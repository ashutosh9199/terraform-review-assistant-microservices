from sqlalchemy import select

from app.core.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.domain import User, UserRole


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == "admin@example.com"))
        if existing:
            print("Admin user already exists.")
            return
        user = User(
            email="admin@example.com",
            password_hash=hash_password("ChangeMe123!"),
            full_name="Platform Admin",
            roles=[UserRole(role="admin"), UserRole(role="reviewer")],
        )
        db.add(user)
        db.commit()
        print("Created admin@example.com with password ChangeMe123!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
