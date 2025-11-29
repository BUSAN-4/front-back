from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

# 인증 코드 상수
CITY_ADMIN_CODE = "BUSAN2024"
SYSTEM_ADMIN_CODE = "SYSTEM2024"


@router.post("/register", response_model=dict)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """회원가입"""
    # username 중복 확인
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 이메일 중복 확인
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 역할 및 인증 코드 검증
    role = UserRole.GENERAL
    if request.role == "city":
        if request.admin_code != CITY_ADMIN_CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid city admin code"
            )
        role = UserRole.CITY
    elif request.role == "admin":
        if request.admin_code != SYSTEM_ADMIN_CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid system admin code"
            )
        role = UserRole.ADMIN
    
    # 사용자 생성
    hashed_password = get_password_hash(request.password)
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password,
        name=request.name,
        phone=request.phone,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 토큰 생성
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = f"refresh-{access_token}"  # 간단한 refresh token
    
    # 사용자 정보 반환
    user_response = UserResponse.from_orm_user(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response.dict()
    }


@router.post("/login", response_model=dict)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """로그인"""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 역할 확인 (frontend에서 전달한 역할과 일치하는지 확인)
    if request.role:
        expected_role = UserRole.GENERAL
        if request.role == "city":
            expected_role = UserRole.CITY
        elif request.role == "admin":
            expected_role = UserRole.ADMIN
        
        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role mismatch"
            )
    
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = f"refresh-{access_token}"
    
    # 사용자 정보 반환
    user_response = UserResponse.from_orm_user(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response.dict()
    }

