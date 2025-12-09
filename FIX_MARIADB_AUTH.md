# MariaDB 인증 플러그인 오류 해결 방법

## 문제
```
(pymysql.err.OperationalError) (2059, "Authentication plugin 'b'auth_gssapi_client'' not configured")
```

이 오류는 MariaDB 서버에서 사용자의 인증 플러그인이 `auth_gssapi_client`로 설정되어 있는데, PyMySQL이 이를 지원하지 않기 때문에 발생합니다.

## 해결 방법

### 방법 1: MariaDB 서버에서 직접 SQL 실행 (권장)

MariaDB 클라이언트(HeidiSQL, DBeaver, MySQL Workbench 등)로 서버에 접속하여 다음 SQL을 실행하세요:

```sql
-- root 사용자의 인증 방식을 mysql_native_password로 변경
ALTER USER 'root'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');

-- 권한 새로고침
FLUSH PRIVILEGES;
```

**참고:**
- `'root'@'%'`: 모든 호스트에서 접속하는 root 사용자
- `'root'@'localhost'`: localhost에서만 접속하는 root 사용자
- `'1234'`: 실제 비밀번호로 변경하세요

### 방법 2: 명령줄에서 실행

MariaDB 서버에 SSH 접속이 가능한 경우:

```bash
mysql -u root -p
```

그 다음 SQL 실행:
```sql
ALTER USER 'root'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
FLUSH PRIVILEGES;
```

### 방법 3: 현재 사용자 확인

먼저 현재 사용자의 인증 플러그인을 확인하세요:

```sql
SELECT user, host, plugin FROM mysql.user WHERE user = 'root';
```

결과 예시:
```
+------+-----------+----------------------+
| user | host      | plugin               |
+------+-----------+----------------------+
| root | %         | auth_gssapi_client   |
| root | localhost | auth_gssapi_client   |
+------+-----------+----------------------+
```

이 경우 위의 ALTER USER 명령을 실행하면 `plugin`이 `mysql_native_password`로 변경됩니다.

### 방법 4: 모든 사용자 일괄 변경

모든 사용자의 인증 방식을 변경하려면:

```sql
-- 모든 사용자 확인
SELECT user, host, plugin FROM mysql.user;

-- 각 사용자별로 실행 (예시)
ALTER USER 'root'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
-- 다른 사용자가 있다면 추가로 실행

FLUSH PRIVILEGES;
```

## 변경 후 확인

변경 후 다시 확인:

```sql
SELECT user, host, plugin FROM mysql.user WHERE user = 'root';
```

결과가 다음과 같이 나와야 합니다:
```
+------+-----------+----------------------+
| user | host      | plugin               |
+------+-----------+----------------------+
| root | %         | mysql_native_password|
| root | localhost | mysql_native_password|
+------+-----------+----------------------+
```

## 애플리케이션 재시작

변경 후 FastAPI 서버를 재시작하세요:

```bash
# 서버 중지 (Ctrl+C)
# 서버 재시작
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 추가 정보

- MariaDB 10.4 이상 버전에서는 기본 인증 플러그인이 변경되었습니다
- PyMySQL은 `mysql_native_password` 플러그인만 지원합니다
- `auth_gssapi_client`, `auth_ed25519` 등은 PyMySQL에서 지원하지 않습니다


