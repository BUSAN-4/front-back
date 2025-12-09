"""
web 데이터베이스 테이블 초기화 스크립트
"""
from app.database import web_engine, Base
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.user_vehicle_mapping import UserVehicleMapping
from app.models.user_log import UserLog  # 로그 테이블 추가
from app.models.arrears_detection_modification import ArrearsDetectionModification  # 체납 탐지 수정 기록 테이블
from app.models.missing_person_detection_modification import MissingPersonDetectionModification  # 실종자 탐지 수정 기록 테이블

def init_web_db():
    """web 데이터베이스에 테이블 생성"""
    print("Creating tables in web database...")
    # 모든 모델을 import하여 Base.metadata에 등록
    Base.metadata.create_all(bind=web_engine)
    print("Tables created successfully!")
    print("Created tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    init_web_db()

