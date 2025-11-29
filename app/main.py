from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.api import auth, users, vehicles, trips, city, admin, test  # test 추가
from app.database import engine, SessionLocal

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI 백엔드 애플리케이션",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(city.router, prefix="/api/city", tags=["city"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(test.router, prefix="/api/test", tags=["test"])  # 추가


@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/health/db")
async def health_check_db():
    """데이터베이스 연결 상태 확인"""
    try:
        # 데이터베이스 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        # 테이블 존재 여부 확인
        db = SessionLocal()
        try:
            # users 테이블 확인
            result = db.execute(text("SHOW TABLES LIKE 'users'"))
            table_exists = result.fetchone() is not None
            
            return {
                "status": "connected",
                "database": "connected",
                "tables_initialized": table_exists,
                "message": "Database connection successful"
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

