"""
MariaDB 인증 플러그인 확인 및 강제 변경 스크립트
"""
import pymysql
from urllib.parse import urlparse

# .env 파일에서 직접 읽기
def parse_db_url(url_str):
    """데이터베이스 URL 파싱"""
    if url_str.startswith('mysql+pymysql://'):
        url_str = url_str.replace('mysql+pymysql://', 'mysql://')
    
    parsed = urlparse(url_str)
    return {
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port or 3306,
        'database': parsed.path.lstrip('/').split('?')[0]
    }

# .env 파일 읽기
try:
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # DATABASE_URL 추출
    db_url = None
    for line in env_content.split('\n'):
        if line.startswith('DATABASE_URL=') and not line.strip().startswith('#'):
            db_url = line.split('=', 1)[1].strip()
            break
    
    if not db_url:
        print("❌ DATABASE_URL을 찾을 수 없습니다.")
        exit(1)
    
    print(f"📋 DATABASE_URL: {db_url}")
    
    # URL 파싱
    db_info = parse_db_url(db_url)
    print(f"\n연결 정보:")
    print(f"  호스트: {db_info['host']}")
    print(f"  포트: {db_info['port']}")
    print(f"  사용자: {db_info['user']}")
    print(f"  데이터베이스: {db_info['database']}")
    
    # MariaDB 연결 시도
    print(f"\n🔌 MariaDB 연결 시도...")
    try:
        conn = pymysql.connect(
            host=db_info['host'],
            port=db_info['port'],
            user=db_info['user'],
            password=db_info['password'],
            database=db_info['database'],
            charset='utf8mb4',
            connect_timeout=10
        )
        print("✅ 연결 성공!")
        
        cursor = conn.cursor()
        
        # 현재 사용자 확인
        cursor.execute("SELECT USER(), @@hostname")
        user_info = cursor.fetchone()
        print(f"\n현재 연결된 사용자: {user_info[0]}")
        print(f"서버 호스트: {user_info[1]}")
        
        # 인증 플러그인 확인
        cursor.execute("""
            SELECT user, host, plugin 
            FROM mysql.user 
            WHERE user = SUBSTRING_INDEX(USER(), '@', 1)
        """)
        plugins = cursor.fetchall()
        
        print(f"\n인증 플러그인 정보:")
        needs_fix = False
        for user, host, plugin in plugins:
            status = "✅" if plugin == "mysql_native_password" else "❌"
            print(f"  {status} {user}@{host}: {plugin}")
            if plugin != "mysql_native_password":
                needs_fix = True
        
        if needs_fix:
            print(f"\n⚠️ 일부 사용자가 mysql_native_password가 아닙니다.")
            print(f"다음 SQL을 MariaDB 서버에서 실행하세요:")
            print(f"\nALTER USER '{db_info['user']}'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('{db_info['password']}');")
            print(f"ALTER USER '{db_info['user']}'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('{db_info['password']}');")
            print(f"FLUSH PRIVILEGES;")
        else:
            print(f"\n✅ 모든 사용자가 mysql_native_password로 설정되어 있습니다.")
            print(f"만약 여전히 오류가 발생한다면 MariaDB 서버를 재시작하세요.")
        
        cursor.close()
        conn.close()
        
    except pymysql.err.OperationalError as e:
        if "2059" in str(e) or "auth_gssapi_client" in str(e):
            print(f"❌ 인증 플러그인 오류 발생!")
            print(f"오류: {e}")
            print(f"\n해결 방법:")
            print(f"1. MariaDB 서버에 접속하여 다음 SQL 실행:")
            print(f"   ALTER USER '{db_info['user']}'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('{db_info['password']}');")
            print(f"   ALTER USER '{db_info['user']}'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('{db_info['password']}');")
            print(f"   FLUSH PRIVILEGES;")
            print(f"\n2. MariaDB 서버 재시작")
            print(f"3. FastAPI 서버 재시작")
        else:
            print(f"❌ 연결 실패: {e}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

except FileNotFoundError:
    print("❌ .env 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"❌ 오류: {e}")
    import traceback
    traceback.print_exc()


