"""
users 테이블의 name 컬럼 문자셋을 utf8mb4로 변경
"""
from sqlalchemy import text
from app.database import web_engine

def fix_name_column():
    """name 컬럼 문자셋 변경"""
    try:
        with web_engine.connect() as connection:
            # name 컬럼 문자셋 변경
            print("name 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
                """))
                connection.commit()
                print("[SUCCESS] name 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"[ERROR] name 컬럼 문자셋 변경 실패: {str(e)}")
                connection.rollback()
                
            # phone 컬럼도 확인 및 변경
            print("phone 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN phone VARCHAR(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """))
                connection.commit()
                print("[SUCCESS] phone 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"[INFO] phone 컬럼 문자셋 변경: {str(e)}")
                
            # organization 컬럼도 확인 및 변경
            print("organization 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN organization VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """))
                connection.commit()
                print("[SUCCESS] organization 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"[INFO] organization 컬럼 문자셋 변경: {str(e)}")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("users 테이블의 한글 컬럼 문자셋 변경 중...")
    fix_name_column()
    print("완료!")

