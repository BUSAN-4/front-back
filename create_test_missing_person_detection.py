"""
실종자 탐지 테스트용 더미 데이터 생성 스크립트
busan_car DB의 missing_person_detection 테이블에 최신 탐지 기록 추가
"""
import os
import sys
from pathlib import Path

# backend 디렉토리를 Python 경로에 추가
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# .env 파일 로드
from dotenv import load_dotenv
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)

from datetime import datetime
from sqlalchemy import create_engine, text
from app.core.config import settings
from sqlalchemy.pool import NullPool
import uuid

# Windows 콘솔에서 유니코드 출력을 위해 인코딩 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# busan_car 데이터베이스 연결
connect_args_busan_car = {
    "charset": "utf8mb4",
    "connect_timeout": 10,
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    "read_default_file": None,
}

busan_car_engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    echo=True,
    connect_args=connect_args_busan_car
)

def create_test_detection():
    """테스트용 실종자 탐지 기록 생성"""
    # 테스트용 데이터
    detection_id = f"test_mp_{uuid.uuid4().hex[:16]}"
    missing_id = f"missing_{uuid.uuid4().hex[:16]}"  # 테스트용 실종자 ID
    detection_success = None  # 미확인 상태
    detected_lat = 35.1796  # 부산 좌표
    detected_lon = 129.0756
    detected_time = datetime.now()  # 현재 시간
    
    with busan_car_engine.connect() as conn:
        # vehicle_exterior_image에서 실제 image_id 가져오기 (없으면 NULL 사용)
        image_result = conn.execute(text("""
            SELECT image_id 
            FROM vehicle_exterior_image 
            LIMIT 1
        """))
        image_row = image_result.fetchone()
        image_id = image_row[0] if image_row else None
        print(f"사용할 image_id: {image_id}")

        # missing_person_info에 해당 실종자가 있는지 확인 (없으면 생성)
        check_info = conn.execute(text("""
            SELECT missing_id 
            FROM missing_person_info 
            WHERE missing_id = :missing_id
        """), {"missing_id": missing_id})
        
        if check_info.fetchone() is None:
            print(f"missing_person_info에 실종자 {missing_id} 추가 중...")
            conn.execute(text("""
                INSERT INTO missing_person_info (missing_id, missing_name, missing_age, missing_identity, registered_at, updated_at, missing_location)
                VALUES (:missing_id, :name, :age, :identity, :registered, :updated, :location)
            """), {
                "missing_id": missing_id,
                "name": "테스트 실종자",
                "age": 30,
                "identity": "테스트용 실종자 정보",
                "registered": datetime.now(),
                "updated": datetime.now(),
                "location": "부산광역시"
            })
            conn.commit()
            print("✓ missing_person_info에 실종자 추가 완료")
        
        # missing_person_detection에 탐지 기록 추가
        print(f"\n탐지 기록 생성 중...")
        print(f"  - detection_id: {detection_id}")
        print(f"  - missing_id: {missing_id}")
        print(f"  - detected_time: {detected_time}")
        
        # image_id가 있으면 포함, 없으면 NULL
        if image_id:
            conn.execute(text("""
                INSERT INTO missing_person_detection 
                (detection_id, image_id, missing_id, detection_success, detected_lat, detected_lon, detected_time)
                VALUES (:detection_id, :image_id, :missing_id, :detection_success, :detected_lat, :detected_lon, :detected_time)
            """), {
                "detection_id": detection_id,
                "image_id": image_id,
                "missing_id": missing_id,
                "detection_success": detection_success,
                "detected_lat": detected_lat,
                "detected_lon": detected_lon,
                "detected_time": detected_time
            })
        else:
            # image_id가 없으면 NULL로 설정 (외래 키 제약 조건이 있을 수 있으므로 주의)
            # 실제로는 image_id가 NOT NULL이면 이 방법은 작동하지 않을 수 있음
            print("⚠ 경고: image_id가 없습니다. image_id를 NULL로 설정합니다.")
            conn.execute(text("""
                INSERT INTO missing_person_detection 
                (detection_id, missing_id, detection_success, detected_lat, detected_lon, detected_time)
                VALUES (:detection_id, :missing_id, :detection_success, :detected_lat, :detected_lon, :detected_time)
            """), {
                "detection_id": detection_id,
                "missing_id": missing_id,
                "detection_success": detection_success,
                "detected_lat": detected_lat,
                "detected_lon": detected_lon,
                "detected_time": detected_time
            })
        conn.commit()
        
        print("\n✓ 탐지 기록 생성 완료!")
        print(f"  탐지 ID: {detection_id}")
        print(f"  실종자 ID: {missing_id}")
        print(f"  탐지 시간: {detected_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n웹 페이지에서 알림이 표시되는지 확인하세요!")

if __name__ == "__main__":
    try:
        create_test_detection()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

