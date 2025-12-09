"""
체납 차량 탐지 테스트용 더미 데이터 생성 스크립트
busan_car DB의 arrears_detection 테이블에 최신 탐지 기록 추가
"""
from datetime import datetime
from sqlalchemy import create_engine, text
from app.core.config import settings
from sqlalchemy.pool import NullPool
import uuid

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
    """테스트용 탐지 기록 생성"""
    # 테스트용 데이터
    detection_id = f"test_{uuid.uuid4().hex[:16]}"
    car_plate_number = "12가3456"  # 테스트용 차량 번호
    detection_success = None  # 미확인 상태
    detected_lat = 35.1796  # 부산 좌표
    detected_lon = 129.0756
    detected_time = datetime.now()  # 현재 시간
    
    with busan_car_engine.connect() as conn:
        # vehicle_exterior_image에서 실제 image_id 가져오기
        image_result = conn.execute(text("""
            SELECT image_id 
            FROM vehicle_exterior_image 
            LIMIT 1
        """))
        image_row = image_result.fetchone()
        
        if not image_row:
            print("오류: vehicle_exterior_image 테이블에 데이터가 없습니다.")
            print("먼저 vehicle_exterior_image 테이블에 데이터를 추가해주세요.")
            return
        
        image_id = image_row[0]
        print(f"사용할 image_id: {image_id}")
        # arrears_info에 해당 차량이 있는지 확인 (없으면 생성)
        check_info = conn.execute(text("""
            SELECT car_plate_number 
            FROM arrears_info 
            WHERE car_plate_number = :plate
        """), {"plate": car_plate_number})
        
        if check_info.fetchone() is None:
            print(f"arrears_info에 차량 {car_plate_number} 추가 중...")
            conn.execute(text("""
                INSERT INTO arrears_info (car_plate_number, arrears_user_id, total_arrears_amount, arrears_period, notice_sent, updated_at)
                VALUES (:plate, :user_id, :amount, :period, :notice, :updated)
            """), {
                "plate": car_plate_number,
                "user_id": f"user_{uuid.uuid4().hex[:16]}",
                "amount": 1000000,
                "period": "2024-01",
                "notice": 0,
                "updated": datetime.now()
            })
            conn.commit()
            print("arrears_info에 차량 추가 완료")
        
        # arrears_detection에 탐지 기록 추가
        print(f"\n탐지 기록 생성 중...")
        print(f"  - detection_id: {detection_id}")
        print(f"  - car_plate_number: {car_plate_number}")
        print(f"  - detected_time: {detected_time}")
        
        # arrears_detection에 탐지 기록 추가
        conn.execute(text("""
            INSERT INTO arrears_detection 
            (detection_id, image_id, car_plate_number, detection_success, detected_lat, detected_lon, detected_time)
            VALUES (:detection_id, :image_id, :car_plate_number, :detection_success, :detected_lat, :detected_lon, :detected_time)
        """), {
            "detection_id": detection_id,
            "image_id": image_id,
            "car_plate_number": car_plate_number,
            "detection_success": detection_success,
            "detected_lat": detected_lat,
            "detected_lon": detected_lon,
            "detected_time": detected_time
        })
        conn.commit()
        
        print("\n탐지 기록 생성 완료!")
        print(f"  탐지 ID: {detection_id}")
        print(f"  차량 번호: {car_plate_number}")
        print(f"  탐지 시간: {detected_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n웹 페이지에서 알림이 표시되는지 확인하세요!")

if __name__ == "__main__":
    try:
        create_test_detection()
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

