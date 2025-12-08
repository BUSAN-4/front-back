"""
vehicles 테이블에 car_id 컬럼 추가 마이그레이션
"""
from sqlalchemy import text
from app.database import web_engine

def add_car_id_to_vehicles():
    """vehicles 테이블에 car_id 컬럼 추가"""
    try:
        with web_engine.connect() as connection:
            # car_id 컬럼이 이미 존재하는지 확인
            result = connection.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'vehicles'
                AND COLUMN_NAME = 'car_id'
            """))
            
            count = result.fetchone()[0]
            
            if count == 0:
                # car_id 컬럼 추가
                connection.execute(text("""
                    ALTER TABLE vehicles
                    ADD COLUMN car_id VARCHAR(255) NULL
                    COMMENT 'busan_car DB의 uservehicle.car_id'
                    AFTER license_plate
                """))
                
                # 인덱스 추가
                try:
                    connection.execute(text("""
                        CREATE INDEX idx_vehicles_car_id ON vehicles(car_id)
                    """))
                except Exception as idx_error:
                    print(f"[WARNING] Index creation: {idx_error}")
                
                connection.commit()
                print("[SUCCESS] car_id 컬럼이 성공적으로 추가되었습니다.")
            else:
                print("[INFO] car_id 컬럼이 이미 존재합니다.")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("vehicles 테이블에 car_id 컬럼 추가 중...")
    add_car_id_to_vehicles()
    print("완료!")

