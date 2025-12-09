"""
MariaDB 인증 플러그인 오류 해결 스크립트
서버에서 직접 실행하여 사용자의 인증 방식을 변경합니다.
"""
import pymysql
from app.core.config import settings

def fix_auth_plugin():
    """MariaDB 사용자의 인증 방식을 mysql_native_password로 변경"""
    try:
        # 연결 URL에서 정보 추출
        db_url = settings.DATABASE_URL
        # mysql+pymysql://user:password@host:port/database 형식 파싱
        if 'mysql+pymysql://' in db_url:
            url_part = db_url.replace('mysql+pymysql://', '')
        else:
            url_part = db_url.replace('mysql://', '')
        
        # @ 기준으로 분리
        auth_part, rest = url_part.split('@', 1)
        user, password = auth_part.split(':', 1)
        
        # 호스트와 포트, 데이터베이스 분리
        if '/' in rest:
            host_port, database = rest.split('/', 1)
            if '?' in database:
                database = database.split('?')[0]
        else:
            host_port = rest.split('?')[0]
            database = None
        
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        print(f"연결 정보:")
        print(f"  호스트: {host}")
        print(f"  포트: {port}")
        print(f"  사용자: {user}")
        print(f"  데이터베이스: {database}")
        
        # MariaDB에 연결 (인증 오류를 우회하기 위해 다른 방법 시도)
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                charset='utf8mb4',
                connect_timeout=10
            )
        except Exception as e:
            print(f"\n❌ 연결 실패: {e}")
            print("\n해결 방법:")
            print("1. MariaDB 서버에 직접 접속하여 다음 SQL을 실행하세요:")
            print(f"   ALTER USER '{user}'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('{password}');")
            print(f"   FLUSH PRIVILEGES;")
            print("\n2. 또는 root로 접속하여:")
            print(f"   ALTER USER '{user}'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('{password}');")
            print(f"   FLUSH PRIVILEGES;")
            return
        
        cursor = conn.cursor()
        
        # 현재 사용자 확인
        cursor.execute("SELECT user, host, plugin FROM mysql.user WHERE user = %s", (user,))
        users = cursor.fetchall()
        
        if not users:
            print(f"\n⚠️ 사용자 '{user}'를 찾을 수 없습니다.")
            cursor.close()
            conn.close()
            return
        
        print(f"\n현재 사용자 정보:")
        for db_user, db_host, plugin in users:
            print(f"  {db_user}@{db_host}: {plugin}")
        
        # 인증 방식 변경
        print(f"\n인증 방식을 mysql_native_password로 변경 중...")
        for db_user, db_host, plugin in users:
            if plugin != 'mysql_native_password':
                try:
                    # 비밀번호를 포함한 ALTER USER 명령
                    sql = f"ALTER USER '{db_user}'@'{db_host}' IDENTIFIED VIA mysql_native_password USING PASSWORD('{password}')"
                    cursor.execute(sql)
                    print(f"✅ {db_user}@{db_host} 인증 방식 변경 완료")
                except Exception as e:
                    print(f"❌ {db_user}@{db_host} 변경 실패: {e}")
        
        # 권한 새로고침
        cursor.execute("FLUSH PRIVILEGES")
        print("\n✅ 권한 새로고침 완료")
        
        cursor.close()
        conn.close()
        print("\n✅ 완료! 이제 애플리케이션을 재시작하세요.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("MariaDB 인증 플러그인 수정 스크립트")
    print("=" * 50)
    fix_auth_plugin()


