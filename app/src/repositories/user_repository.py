from sqlalchemy.orm import Session
from app.src.models.users import User
from app.src.schemas.auth import UserCreate
import uuid

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
