"""
데이터베이스 연결 테스트 스크립트

이 스크립트는 backend/.env 파일의 설정을 사용하여 MariaDB 연결을 테스트합니다.
"""

import os
import sys
from pathlib import Path

# backend 디렉토리를 Python 경로에 추가
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from app.core.config import settings
    from app.database import busan_car_engine, web_engine
    import pymysql
except ImportError as e:
    print(f"❌ Import 오류: {e}")
    print("backend 디렉토리에서 실행하세요: cd backend && python test_db_connection.py")
    sys.exit(1)

def test_connection(engine, db_name):
    """데이터베이스 연결 테스트"""
    print(f"\n{'='*60}")
    print(f"[{db_name}] 연결 테스트")
    print(f"{'='*60}")
    
    try:
        # 연결 시도
        with engine.connect() as conn:
            print(f"✅ [{db_name}] 연결 성공!")
            
            # 간단한 쿼리 실행
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                print(f"✅ [{db_name}] 쿼리 실행 성공!")
                return True
            else:
                print(f"⚠️  [{db_name}] 쿼리 결과가 예상과 다릅니다.")
                return False
                
    except pymysql.err.OperationalError as e:
        error_code = e.args[0] if e.args else None
        error_msg = str(e)
        
        if error_code == 2059:
            print(f"❌ [{db_name}] 인증 플러그인 오류!")
            print(f"   오류: {error_msg}")
            print()
            print("해결 방법:")
            print("1. DBeaver에서 fix_mariadb_auth_plugin.sql 실행")
            print("2. MariaDB 서버 재시작 (restart_mariadb.bat)")
            return False
        elif error_code == 1045:
            print(f"❌ [{db_name}] 인증 실패 (비밀번호 오류)")
            print(f"   오류: {error_msg}")
            print()
            print("해결 방법:")
            print("1. backend/.env 파일의 DATABASE_PASSWORD 확인")
            print("2. MariaDB root 비밀번호가 올바른지 확인")
            return False
        else:
            print(f"❌ [{db_name}] 연결 오류!")
            print(f"   오류 코드: {error_code}")
            print(f"   오류 메시지: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ [{db_name}] 예상치 못한 오류!")
        print(f"   오류 타입: {type(e).__name__}")
        print(f"   오류 메시지: {str(e)}")
        return False

def main():
    print("="*60)
    print("MariaDB 연결 테스트")
    print("="*60)
    
    # 설정 정보 출력 (비밀번호는 마스킹)
    print(f"\n[설정 정보]")
    db_url = settings.DATABASE_URL
    # 비밀번호 마스킹
    if '@' in db_url and ':' in db_url:
        parts = db_url.split('@')
        if len(parts) == 2:
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user, _ = user_pass.split(':', 1)
                masked_url = db_url.replace(user_pass, f"{user}:***")
                print(f"  DATABASE_URL: {masked_url}")
            else:
                print(f"  DATABASE_URL: {db_url}")
        else:
            print(f"  DATABASE_URL: {db_url}")
    else:
        print(f"  DATABASE_URL: {db_url}")
    
    web_db_url = settings.WEB_DATABASE_URL or settings.DATABASE_URL.replace('/busan_car', '/web')
    if '@' in web_db_url and ':' in web_db_url:
        parts = web_db_url.split('@')
        if len(parts) == 2:
            user_pass = parts[0].split('//')[-1]
            if ':' in user_pass:
                user, _ = user_pass.split(':', 1)
                masked_url = web_db_url.replace(user_pass, f"{user}:***")
                print(f"  WEB_DATABASE_URL: {masked_url}")
            else:
                print(f"  WEB_DATABASE_URL: {web_db_url}")
        else:
            print(f"  WEB_DATABASE_URL: {web_db_url}")
    else:
        print(f"  WEB_DATABASE_URL: {web_db_url}")
    
    # 연결 테스트
    busan_car_success = test_connection(busan_car_engine, "busan_car")
    web_success = test_connection(web_engine, "web")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("[테스트 결과 요약]")
    print(f"{'='*60}")
    print(f"busan_car DB: {'✅ 성공' if busan_car_success else '❌ 실패'}")
    print(f"web DB:       {'✅ 성공' if web_success else '❌ 실패'}")
    print(f"{'='*60}")
    
    if busan_car_success and web_success:
        print("\n✅ 모든 데이터베이스 연결이 성공했습니다!")
        return 0
    else:
        print("\n❌ 일부 데이터베이스 연결에 실패했습니다.")
        print("위의 해결 방법을 참고하여 문제를 해결하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
