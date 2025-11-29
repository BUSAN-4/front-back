from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# MariaDB/MySQL 연결 설정
# pool_pre_ping=True: 연결이 끊어졌을 때 자동으로 재연결
# pool_recycle=3600: 1시간마다 연결을 재생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG  # 디버그 모드에서 SQL 쿼리 로그 출력
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """데이터베이스 테이블 생성"""
    # 모든 모델을 import하여 Base.metadata에 등록
    from app.models import user, vehicle, trip, violation, missing_person
    # 테이블 생성
    Base.metadata.create_all(bind=engine)

