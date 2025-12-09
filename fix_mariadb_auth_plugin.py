"""
MariaDB 인증 플러그인을 mysql_native_password로 변경하는 스크립트

이 스크립트는 MariaDB 서버에 직접 연결하여 root 사용자의 인증 플러그인을 변경합니다.
주의: 이 스크립트를 실행하기 전에 MariaDB 서버가 실행 중이어야 합니다.

사용법:
    python fix_mariadb_auth_plugin.py
"""

import pymysql
import sys
from getpass import getpass

# MariaDB 연결 정보
DB_HOST = "172.16.11.114"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "1234"  # .env 파일의 비밀번호와 동일하게 설정

def fix_auth_plugin():
    """root 사용자의 인증 플러그인을 mysql_native_password로 변경"""
    try:
        print("=" * 60)
        print("MariaDB 인증 플러그인 변경 스크립트")
        print("=" * 60)
        print()
        
        # MariaDB에 연결 (임시로 다른 인증 방식 시도)
        print(f"[1/5] MariaDB 서버에 연결 중... ({DB_HOST}:{DB_PORT})")
        try:
            # 먼저 mysql_native_password로 연결 시도
            connection = pymysql.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                charset='utf8mb4',
                connect_timeout=10
            )
            print("✅ 연결 성공!")
        except pymysql.err.OperationalError as e:
            if "2059" in str(e) or "auth_gssapi_client" in str(e):
                print("⚠️  인증 플러그인 오류 발생. 다른 방법으로 시도합니다...")
                # 다른 인증 방식으로 연결 시도 (실패할 수 있음)
                print("❌ 현재 인증 플러그인으로는 연결할 수 없습니다.")
                print()
                print("=" * 60)
                print("해결 방법:")
                print("=" * 60)
                print("1. DBeaver에서 MariaDB 서버에 연결")
                print("2. fix_mariadb_auth_plugin.sql 파일의 SQL을 실행")
                print("3. MariaDB 서버를 재시작 (restart_mariadb.bat 사용)")
                print("4. 이 스크립트를 다시 실행")
                return False
            else:
                raise
        
        with connection.cursor() as cursor:
            # 현재 인증 플러그인 확인
            print()
            print("[2/5] 현재 인증 플러그인 확인 중...")
            cursor.execute("""
                SELECT user, host, plugin 
                FROM mysql.user 
                WHERE user = 'root'
            """)
            results = cursor.fetchall()
            print("현재 root 사용자 인증 플러그인:")
            for user, host, plugin in results:
                print(f"  - {user}@{host}: {plugin}")
            
            # 인증 플러그인 변경
            print()
            print("[3/5] 인증 플러그인을 mysql_native_password로 변경 중...")
            
            # 모든 root 사용자에 대해 변경
            hosts_to_fix = ['localhost', '%', '127.0.0.1']
            for host in hosts_to_fix:
                try:
                    sql = f"ALTER USER 'root'@'{host}' IDENTIFIED VIA mysql_native_password USING PASSWORD(%s)"
                    cursor.execute(sql, (DB_PASSWORD,))
                    print(f"  ✅ root@{host} 변경 완료")
                except Exception as e:
                    print(f"  ⚠️  root@{host} 변경 실패: {e}")
            
            # 권한 새로고침
            print()
            print("[4/5] 권한 새로고침 중...")
            cursor.execute("FLUSH PRIVILEGES")
            print("✅ 권한 새로고침 완료")
            
            # 변경 확인
            print()
            print("[5/5] 변경 사항 확인 중...")
            cursor.execute("""
                SELECT user, host, plugin 
                FROM mysql.user 
                WHERE user = 'root'
            """)
            results = cursor.fetchall()
            print("변경 후 root 사용자 인증 플러그인:")
            all_mysql_native = True
            for user, host, plugin in results:
                status = "✅" if plugin == "mysql_native_password" else "❌"
                print(f"  {status} {user}@{host}: {plugin}")
                if plugin != "mysql_native_password":
                    all_mysql_native = False
        
        connection.close()
        
        print()
        print("=" * 60)
        if all_mysql_native:
            print("✅ 모든 root 사용자의 인증 플러그인이 변경되었습니다!")
            print()
            print("⚠️  중요: MariaDB 서버를 재시작해야 변경 사항이 적용됩니다.")
            print("   - restart_mariadb.bat 파일을 관리자 권한으로 실행하세요")
            print("   - 또는 Windows 서비스 관리자에서 MariaDB 서비스를 재시작하세요")
        else:
            print("⚠️  일부 사용자의 인증 플러그인 변경에 실패했습니다.")
            print("   DBeaver에서 fix_mariadb_auth_plugin.sql을 직접 실행하세요.")
        print("=" * 60)
        
        return all_mysql_native
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ 오류 발생:")
        print("=" * 60)
        print(f"{type(e).__name__}: {e}")
        print()
        print("해결 방법:")
        print("1. MariaDB 서버가 실행 중인지 확인")
        print("2. 연결 정보(호스트, 포트, 비밀번호)가 올바른지 확인")
        print("3. DBeaver에서 fix_mariadb_auth_plugin.sql을 직접 실행")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = fix_auth_plugin()
    sys.exit(0 if success else 1)

