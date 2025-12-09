# MariaDB 서버 재시작 가이드

## 문제
인증 플러그인을 `mysql_native_password`로 변경했는데도 여전히 `auth_gssapi_client` 오류가 발생하는 경우, **MariaDB 서버를 재시작**해야 합니다.

## Windows에서 MariaDB 서비스 재시작

### 방법 1: 서비스 관리자 사용
1. `Win + R` 키를 눌러 실행 창 열기
2. `services.msc` 입력 후 Enter
3. "MariaDB" 또는 "MySQL" 서비스 찾기
4. 서비스 우클릭 → "다시 시작"

### 방법 2: 명령 프롬프트 (관리자 권한)
```cmd
# 서비스 중지
net stop MariaDB

# 서비스 시작
net start MariaDB
```

또는 MySQL인 경우:
```cmd
net stop MySQL
net start MySQL
```

### 방법 3: PowerShell (관리자 권한)
```powershell
# 서비스 재시작
Restart-Service -Name MariaDB

# 또는 MySQL인 경우
Restart-Service -Name MySQL
```

## 재시작 후 확인

1. **FastAPI 서버 재시작**
   ```bash
   # 현재 서버 중지 (Ctrl+C)
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **연결 테스트**
   - 회원가입이나 로그인을 다시 시도해보세요.

## 추가 확인 사항

MariaDB에 접속하여 다시 확인:

```sql
-- 인증 플러그인 확인
SELECT user, host, plugin FROM mysql.user WHERE user = 'root';

-- 모든 root 사용자가 mysql_native_password인지 확인
-- 만약 여전히 auth_gssapi_client가 있다면:
ALTER USER 'root'@'%' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('1234');
FLUSH PRIVILEGES;
```

## 중요
- 인증 플러그인 변경 후 **반드시 MariaDB 서버를 재시작**해야 합니다.
- 서버 재시작 없이는 변경사항이 적용되지 않습니다.


