from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.src.database import get_db
from app.src.repositories.user_repository import UserRepository
from app.src.services.auth_service import AuthService
from app.src.schemas.auth import UserCreate, UserResponse, Token
from typing import Annotated

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        return auth_service.sign_up(user_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred during user registration"
        )

@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        return auth_service.authenticate_user(form_data.username, form_data.password)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred during login process"
        )
