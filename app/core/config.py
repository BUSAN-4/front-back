from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 데이터베이스 설정
    DATABASE_URL: str  # busan_car (읽기 전용 - 데이터 조회용)
    WEB_DATABASE_URL: Optional[str] = None  # web (쓰기 전용 - 웹에서 새롭게 저장할 데이터만)
    
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24시간 (개발 환경에서 편의를 위해)
    
    # 기타 설정
    PROJECT_NAME: str = "FastAPI Backend"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

