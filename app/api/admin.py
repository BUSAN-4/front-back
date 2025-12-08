from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.api.deps import require_system_admin
from app.models.user import User, UserRole
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/users", response_model=List[dict])
async def get_all_users(
    search: Optional[str] = Query(None, description="검색어 (username, name, email)"),
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """모든 사용자 조회 (시스템 관리자)"""
    query = db.query(User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.like(search_term)) |
            (User.email.like(search_term))
        )
    
    users = query.all()
    return [UserResponse.from_orm_user(user).dict() for user in users]


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """사용자 삭제 (시스템 관리자)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 자기 자신은 삭제 불가
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    db.delete(user)
    db.commit()
    return None


@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """사용자 권한 변경 (시스템 관리자)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # role 문자열을 UserRole enum으로 변환
    role_map = {
        "GENERAL": UserRole.GENERAL,
        "ADMIN": UserRole.ADMIN,
        "user": UserRole.GENERAL,  # 하위 호환성
        "admin": UserRole.ADMIN    # 하위 호환성
    }
    
    if role not in role_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    user.role = role_map[role]
    db.commit()
    db.refresh(user)
    
    user_response = UserResponse.from_orm_user(user)
    return user_response.dict()

