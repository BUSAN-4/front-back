"""
user_vehicle_mapping 테이블의 문자셋 수정
"""
from sqlalchemy import text
from app.database import web_engine

def fix_user_vehicle_mapping_charset():
    """user_vehicle_mapping 테이블의 문자셋을 utf8mb4로 변경"""
    try:
        with web_engine.connect() as connection:
            # car_plate_number 컬럼 문자셋 변경
            connection.execute(text("""
                ALTER TABLE user_vehicle_mapping
                MODIFY COLUMN car_plate_number VARCHAR(20) 
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
            """))
            
            # car_id 컬럼 문자셋 변경
            connection.execute(text("""
                ALTER TABLE user_vehicle_mapping
                MODIFY COLUMN car_id VARCHAR(255) 
                CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
            """))
            
            connection.commit()
            print("[SUCCESS] user_vehicle_mapping 테이블의 문자셋이 성공적으로 수정되었습니다.")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("user_vehicle_mapping 테이블의 문자셋 수정 중...")
    fix_user_vehicle_mapping_charset()
    print("완료!")


