"""
users 테이블 구조 확인 스크립트
"""
from sqlalchemy import text, inspect
from app.database import web_engine

def check_users_table():
    """users 테이블 구조 확인"""
    try:
        with web_engine.connect() as connection:
            # 테이블 구조 확인
            result = connection.execute(text("""
                DESCRIBE users
            """))
            
            print("users 테이블 구조:")
            print("-" * 80)
            for row in result.fetchall():
                print(f"컬럼명: {row[0]}, 타입: {row[1]}, NULL 허용: {row[2]}, 기본값: {row[4]}")
            print("-" * 80)
                
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    check_users_table()

