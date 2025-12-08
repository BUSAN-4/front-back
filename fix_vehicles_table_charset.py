"""
vehicles 테이블의 license_plate 컬럼 문자셋을 utf8mb4로 변경
"""
from sqlalchemy import text
from app.database import web_engine

def fix_vehicles_table_charset():
    """vehicles 테이블의 한글 컬럼 문자셋 변경"""
    try:
        with web_engine.connect() as connection:
            # license_plate 컬럼 문자셋 변경
            print("license_plate 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE vehicles 
                    MODIFY COLUMN license_plate VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
                """))
                connection.commit()
                print("[SUCCESS] license_plate 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"[ERROR] license_plate 컬럼 문자셋 변경 실패: {str(e)}")
                connection.rollback()
                
            # model 컬럼도 확인 및 변경
            print("model 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE vehicles 
                    MODIFY COLUMN model VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """))
                connection.commit()
                print("[SUCCESS] model 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"[INFO] model 컬럼 문자셋 변경: {str(e)}")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("vehicles 테이블의 한글 컬럼 문자셋 변경 중...")
    fix_vehicles_table_charset()
    print("완료!")

