"""
데이터베이스 연결 테스트 스크립트

사용법:
    python test_db_connection.py
"""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 환경 변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv가 설치되지 않았습니다. 환경 변수를 직접 설정하세요.")

from app.core.config import settings


def test_connection():
    """데이터베이스 연결 테스트"""
    print("=" * 50)
    print("데이터베이스 연결 테스트 시작")
    print("=" * 50)
    
    try:
        print(f"\n1. DATABASE_URL 확인 중...")
        print(f"   URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'N/A'}")
        
        print(f"\n2. 데이터베이스 연결 시도 중...")
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        with engine.connect() as connection:
            print("   ✓ 연결 성공!")
            
            # 간단한 쿼리 실행
            print(f"\n3. 쿼리 테스트 중...")
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"   ✓ 데이터베이스 버전: {version}")
            
            # 현재 데이터베이스 확인
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"   ✓ 현재 데이터베이스: {db_name}")
            
            # 테이블 목록 확인
            print(f"\n4. 테이블 목록 확인 중...")
            result = connection.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"   ✓ 발견된 테이블 ({len(tables)}개):")
                for table in tables:
                    print(f"     - {table}")
            else:
                print("   ⚠ 테이블이 없습니다. 애플리케이션을 실행하면 자동으로 생성됩니다.")
            
            # users 테이블 구조 확인 (존재하는 경우)
            if 'users' in tables:
                print(f"\n5. users 테이블 구조 확인 중...")
                result = connection.execute(text("DESCRIBE users"))
                columns = result.fetchall()
                print(f"   ✓ 컬럼 목록:")
                for col in columns:
                    print(f"     - {col[0]} ({col[1]})")
        
        print("\n" + "=" * 50)
        print("✓ 모든 테스트 통과! 데이터베이스 연결이 정상입니다.")
        print("=" * 50)
        return True
        
    except SQLAlchemyError as e:
        print("\n" + "=" * 50)
        print("✗ 데이터베이스 연결 실패!")
        print("=" * 50)
        print(f"\n오류 내용: {str(e)}")
        print("\n확인 사항:")
        print("1. .env 파일에 DATABASE_URL이 올바르게 설정되어 있는지 확인")
        print("2. MariaDB/MySQL 서버가 실행 중인지 확인")
        print("3. 데이터베이스가 생성되어 있는지 확인")
        print("4. 사용자 이름과 비밀번호가 올바른지 확인")
        print("5. 방화벽 설정 확인")
        return False
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("✗ 예상치 못한 오류 발생!")
        print("=" * 50)
        print(f"\n오류 내용: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

