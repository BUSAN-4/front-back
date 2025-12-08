"""
데이터베이스와 테이블의 문자셋 확인
"""
from sqlalchemy import text
from app.database import web_engine

def check_charset():
    """데이터베이스와 테이블 문자셋 확인"""
    try:
        with web_engine.connect() as connection:
            # 데이터베이스 문자셋 확인
            print("=== 데이터베이스 문자셋 ===")
            result = connection.execute(text("""
                SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
                FROM information_schema.SCHEMATA
                WHERE SCHEMA_NAME = DATABASE()
            """))
            db_info = result.fetchone()
            print(f"데이터베이스: {db_info[0]} / {db_info[1]}")
            
            # users 테이블 문자셋 확인
            print("\n=== users 테이블 문자셋 ===")
            result = connection.execute(text("""
                SELECT TABLE_COLLATION
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
            """))
            table_info = result.fetchone()
            print(f"테이블: {table_info[0] if table_info else 'N/A'}")
            
            # users 테이블의 모든 컬럼 문자셋 확인
            print("\n=== users 테이블 컬럼 문자셋 ===")
            result = connection.execute(text("""
                SELECT COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'users'
                AND CHARACTER_SET_NAME IS NOT NULL
                ORDER BY ORDINAL_POSITION
            """))
            for row in result.fetchall():
                print(f"{row[0]}: {row[1]} / {row[2]}")
                
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    check_charset()

