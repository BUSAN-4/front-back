from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str
    role: Optional[str] = None  # frontend에서 전달하는 역할 (선택적)


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: str = "general"  # general, city, admin
    admin_code: Optional[str] = None  # city/admin 가입 시 인증 코드


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

