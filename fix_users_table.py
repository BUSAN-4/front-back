"""
users 테이블 수정 스크립트
1. username 컬럼 문자셋을 utf8mb4로 변경
2. role enum을 GENERAL, ADMIN만 사용하도록 변경
"""
from sqlalchemy import text
from app.database import web_engine

def fix_users_table():
    """users 테이블 수정"""
    try:
        with web_engine.connect() as connection:
            # 1. username 컬럼 문자셋 변경
            print("1. username 컬럼 문자셋 변경 중...")
            try:
                connection.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN username VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
                """))
                print("   [SUCCESS] username 컬럼 문자셋 변경 완료")
            except Exception as e:
                print(f"   [INFO] username 컬럼 문자셋 변경: {str(e)}")
            
            # 2. role enum 타입 변경 (GENERAL, ADMIN만)
            print("2. role enum 타입 변경 중...")
            try:
                # 기존 데이터 백업 및 변환
                connection.execute(text("""
                    UPDATE users 
                    SET role = CASE 
                        WHEN role = 'CITY' THEN 'ADMIN'
                        WHEN role = 'GENERAL' THEN 'GENERAL'
                        WHEN role = 'ADMIN' THEN 'ADMIN'
                        ELSE 'GENERAL'
                    END
                """))
                
                # enum 타입 변경
                connection.execute(text("""
                    ALTER TABLE users 
                    MODIFY COLUMN role ENUM('GENERAL', 'ADMIN') NOT NULL DEFAULT 'GENERAL'
                """))
                connection.commit()
                print("   [SUCCESS] role enum 타입 변경 완료")
            except Exception as e:
                print(f"   [ERROR] role enum 타입 변경 실패: {str(e)}")
                connection.rollback()
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("users 테이블 수정 중...")
    fix_users_table()
    print("완료!")

