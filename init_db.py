"""
데이터베이스 초기화 스크립트

테이블을 생성하고 초기 데이터를 설정합니다.

사용법:
    python init_db.py
"""

import sys
from app.database import init_db, engine
from sqlalchemy import text
from app.core.config import settings


def check_database_exists():
    """데이터베이스 존재 여부 확인"""
    try:
        # DATABASE_URL에서 데이터베이스 이름 추출
        db_url = settings.DATABASE_URL
        if 'mysql+pymysql://' in db_url:
            # mysql+pymysql://user:pass@host:port/dbname 형식
            parts = db_url.split('/')
            if len(parts) > 1:
                db_name = parts[-1].split('?')[0]
                return db_name
        return None
    except Exception:
        return None


def create_tables():
    """테이블 생성"""
    print("=" * 50)
    print("데이터베이스 테이블 생성 시작")
    print("=" * 50)
    
    try:
        print("\n1. 데이터베이스 연결 확인 중...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        print("   ✓ 연결 성공!")
        
        print("\n2. 테이블 생성 중...")
        init_db()
        print("   ✓ 테이블 생성 완료!")
        
        print("\n3. 생성된 테이블 확인 중...")
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"   ✓ 생성된 테이블 ({len(tables)}개):")
                for table in tables:
                    print(f"     - {table}")
            else:
                print("   ⚠ 테이블이 생성되지 않았습니다.")
        
        print("\n" + "=" * 50)
        print("✓ 데이터베이스 초기화 완료!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("✗ 데이터베이스 초기화 실패!")
        print("=" * 50)
        print(f"\n오류 내용: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n주의: 이 스크립트는 기존 테이블을 삭제하지 않습니다.")
    print("테이블이 이미 존재하는 경우 아무 작업도 수행하지 않습니다.\n")
    
    success = create_tables()
    sys.exit(0 if success else 1)

