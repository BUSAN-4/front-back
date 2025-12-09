from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 로그인 로직
    pass

@router.post("/register", response_model=TokenResponse)
def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    # 회원가입 로직
    pass


