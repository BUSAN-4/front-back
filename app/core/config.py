from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 데이터베이스
    DATABASE_URL: str  # 환경 변수에서 로드
    
    # JWT
    SECRET_KEY: str  # 환경 변수에서 로드
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()


