from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# busan_car 데이터베이스 연결 (읽기 전용 - 데이터 조회용)
# pool_pre_ping=True: 연결이 끊어졌을 때 자동으로 재연결
# pool_recycle=3600: 1시간마다 연결을 재생성
busan_car_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG  # 디버그 모드에서 SQL 쿼리 로그 출력
)
BusanCarSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=busan_car_engine)

# web 데이터베이스 연결 (쓰기 전용 - 웹에서 새롭게 저장할 데이터만)
# WEB_DATABASE_URL이 없으면 DATABASE_URL을 사용 (하위 호환성)
web_db_url = settings.WEB_DATABASE_URL or settings.DATABASE_URL.replace('/busan_car', '/web')
web_engine = create_engine(
    web_db_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)
WebSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=web_engine)

# Base는 web DB용으로 사용 (테이블 생성용)
Base = declarative_base()

# busan_car DB용 Base (읽기 전용이므로 테이블 생성 안 함)
BusanCarBase = declarative_base()


def get_busan_car_db():
    """busan_car 데이터베이스 세션 의존성 (읽기 전용 - 데이터 조회용)"""
    db = BusanCarSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_web_db():
    """web 데이터베이스 세션 의존성 (쓰기 전용 - 웹에서 새롭게 저장할 데이터만)"""
    db = WebSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 하위 호환성을 위한 별칭
def get_db():
    """기본 데이터베이스 세션 (web DB 사용)"""
    return get_web_db()


def init_db():
    """데이터베이스 테이블 생성 (기존 테이블 사용하므로 주석 처리)"""
    # 실제 DB 테이블을 사용하므로 테이블 생성은 하지 않음
    # 모든 모델을 import하여 Base.metadata에 등록
    from app.models import (
        user, user_vehicle, car_plate_info, driving_session,
        driving_session_info, missing_person_detection,
        drowsy_drive, arrears_detection
    )
    # 테이블은 이미 존재하므로 생성하지 않음
    # Base.metadata.create_all(bind=engine)

