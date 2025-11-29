from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.GENERAL


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: str  # frontend는 string으로 사용
    username: str
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    role: str  # frontend는 string으로 사용
    createdAt: str  # ISO format string
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_user(cls, user):
        """ORM User 객체를 UserResponse로 변환"""
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            name=user.name,
            phone=user.phone,
            role=user.role.value,
            createdAt=user.created_at.isoformat() if user.created_at else ""
        )

