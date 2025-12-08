"""
users 테이블에 organization 컬럼 추가 마이그레이션 스크립트
"""
from sqlalchemy import text
from app.database import web_engine

def add_organization_column():
    """users 테이블에 organization 컬럼 추가"""
    try:
        with web_engine.connect() as connection:
            # 컬럼이 이미 존재하는지 확인
            result = connection.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND COLUMN_NAME = 'organization'
            """))
            count = result.fetchone()[0]
            
            if count == 0:
                # organization 컬럼 추가
                connection.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN organization VARCHAR(50) NULL
                    COMMENT 'busan, nts, police, system'
                """))
                connection.commit()
                print("[SUCCESS] organization 컬럼이 성공적으로 추가되었습니다.")
            else:
                print("[INFO] organization 컬럼이 이미 존재합니다.")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    print("users 테이블에 organization 컬럼 추가 중...")
    add_organization_column()
    print("완료!")

