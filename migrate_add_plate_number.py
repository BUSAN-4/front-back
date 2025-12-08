"""
user_vehicle_mapping 테이블에 car_plate_number 컬럼 추가 마이그레이션
"""
from sqlalchemy import text
from app.database import web_engine

def migrate_add_plate_number():
    """user_vehicle_mapping 테이블에 car_plate_number 컬럼 추가"""
    print("Adding car_plate_number column to user_vehicle_mapping table...")
    
    with web_engine.begin() as connection:  # begin()을 사용하면 자동으로 commit/rollback 처리
        try:
            # 컬럼이 이미 존재하는지 확인
            result = connection.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'user_vehicle_mapping'
                AND COLUMN_NAME = 'car_plate_number'
            """))
            
            count = result.fetchone()[0]
            
            if count == 0:
                # 컬럼 추가
                connection.execute(text("""
                    ALTER TABLE user_vehicle_mapping
                    ADD COLUMN car_plate_number VARCHAR(20) NOT NULL DEFAULT '' AFTER user_id
                """))
                
                # 인덱스 추가 (별도로 실행)
                try:
                    connection.execute(text("""
                        CREATE INDEX idx_car_plate_number ON user_vehicle_mapping(car_plate_number)
                    """))
                except Exception as idx_error:
                    # 인덱스가 이미 존재할 수 있음
                    print(f"[WARNING] Index creation: {idx_error}")
                
                print("[SUCCESS] car_plate_number column added successfully!")
            else:
                print("[INFO] car_plate_number column already exists.")
                
        except Exception as e:
            print(f"[ERROR] {e}")
            raise

if __name__ == "__main__":
    migrate_add_plate_number()

