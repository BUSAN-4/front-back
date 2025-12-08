from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api import auth, users, vehicles, trips, city, admin, test, user_safety  # test 추가
from app.database import busan_car_engine, BusanCarSessionLocal

app = FastAPI(
    title="FastAPI Backend",
    description="FastAPI 백엔드 애플리케이션",
    version="1.0.0"
)

# CORS 설정 - 모든 응답에 CORS 헤더 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 전역 예외 핸들러 - 모든 예외에 CORS 헤더 추가
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """모든 예외에 CORS 헤더를 추가하는 전역 예외 핸들러"""
    if isinstance(exc, HTTPException):
        response = JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    else:
        response = JSONResponse(
            status_code=500,
            content={"detail": str(exc)}
        )
    
    # CORS 헤더 추가
    origin = request.headers.get("origin")
    if origin and origin in [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# API 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(city.router, prefix="/api/city", tags=["city"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(test.router, prefix="/api/test", tags=["test"])  # 추가
app.include_router(user_safety.router, prefix="/api/user", tags=["user-safety"])


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
        with busan_car_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        # 테이블 존재 여부 확인
        db = BusanCarSessionLocal()
        try:
            # 주요 테이블 확인
            result = db.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            return {
                "status": "connected",
                "database": "connected",
                "tables": tables,
                "table_count": len(tables),
                "message": "Database connection successful"
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

