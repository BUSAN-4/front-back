from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, vehicles
from app.database import engine, Base

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="부산시 스마트 도시 차량 서비스 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터
app.include_router(auth.router, prefix="/api/auth", tags=["인증"])
app.include_router(users.router, prefix="/api/users", tags=["사용자"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["차량"])

@app.get("/")
def root():
    return {"message": "부산시 스마트 도시 차량 서비스 API"}

@app.get("/health")
def health():
    return {"status": "ok"}


