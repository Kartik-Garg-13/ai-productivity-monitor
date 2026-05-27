from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User


def seed_admin(db: Session):
    existing = db.query(User).filter(User.email == "admin@goldilocks.tech").first()
    if existing:
        return
    admin = User(
        name="System Admin",
        email="admin@goldilocks.tech",
        password=get_password_hash("Admin@123"),
        role="admin",
        department="Management",
    )
    db.add(admin)
    db.commit()
