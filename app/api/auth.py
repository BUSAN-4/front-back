from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_web_db
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()


def get_role_from_organization(user_type: str, organization: str = None) -> UserRole:
    """userType으로 UserRole 결정 (GENERAL 또는 ADMIN)"""
    if user_type == "admin":
        return UserRole.ADMIN
    else:
        return UserRole.GENERAL


@router.post("/register", response_model=dict)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_web_db)
):
    """회원가입"""
    # 이메일 중복 확인
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 역할 결정
    role = get_role_from_organization(request.role, request.organization)
    
    # 사용자 생성
    hashed_password = get_password_hash(request.password)
    user = User(
        username=request.name,  # username은 중복 가능 (name과 동일)
        email=request.email,    # email만 고유해야 함
        hashed_password=hashed_password,
        name=request.name,
        phone=request.phone,
        role=role,
        organization=request.organization
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 토큰 생성 (JWT 표준에 따라 sub는 문자열이어야 함)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = f"refresh-{access_token}"
    
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
    db: Session = Depends(get_web_db)
):
    """로그인"""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 비밀번호 검증
    if not verify_password(request.password, user.hashed_password):
        print(f"Password verification failed for user: {user.email}")
        print(f"Stored hash: {user.hashed_password[:50]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 역할 확인 (frontend에서 전달한 역할과 일치하는지 확인)
    # userType이 제공된 경우에만 확인 (선택적)
    if request.userType:
        expected_role = get_role_from_organization(request.userType, request.organization)
        
        if user.role != expected_role:
            # 역할이 일치하지 않아도 로그인은 허용하되, 경고만 표시
            # 또는 실제 DB에 저장된 역할을 우선시
            pass  # 일단 로그인 허용 (DB에 저장된 실제 역할 사용)
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = f"refresh-{access_token}"
    
    # 사용자 정보 반환
    user_response = UserResponse.from_orm_user(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response.dict()
    }

