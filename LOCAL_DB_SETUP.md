# 로컬 MariaDB 연결 설정 가이드

## 1. MariaDB 설치 확인

로컬에 MariaDB가 설치되어 있는지 확인하세요:

```bash
# Windows (PowerShell)
Get-Service -Name "*mariadb*" -ErrorAction SilentlyContinue

# 또는 MySQL 서비스 확인 (MariaDB는 MySQL과 호환)
Get-Service -Name "*mysql*" -ErrorAction SilentlyContinue
```

## 2. 데이터베이스 생성

MariaDB에 접속하여 필요한 데이터베이스를 생성하세요:

```sql
-- MariaDB 접속 (root 사용자)
mysql -u root -p

-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS busan_car CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 권한 확인 (필요시)
SHOW DATABASES;
```

## 3. 환경 변수 설정

`backend/.env` 파일을 생성하거나 수정하세요:

```env
# 로컬 MariaDB 연결 설정
# 포트는 기본값 3306 (다른 포트를 사용하는 경우 변경)
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/busan_car?charset=utf8mb4
WEB_DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/web?charset=utf8mb4

# JWT 설정
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 애플리케이션 설정
PROJECT_NAME=FastAPI Backend
DEBUG=True
```

**중요:**
- `your_password`를 실제 MariaDB root 비밀번호로 변경하세요
- 비밀번호에 특수문자가 포함된 경우 URL 인코딩이 필요할 수 있습니다
- 포트가 3306이 아닌 경우 포트 번호를 변경하세요

## 4. 연결 테스트

연결이 제대로 되는지 테스트하세요:

```bash
cd backend
python -c "from app.database import busan_car_engine, web_engine; print('busan_car DB 연결 성공!' if busan_car_engine else '연결 실패'); print('web DB 연결 성공!' if web_engine else '연결 실패')"
```

또는 간단한 테스트 스크립트:

```python
# test_local_db.py
from app.database import busan_car_engine, web_engine

try:
    with busan_car_engine.connect() as conn:
        print("✅ busan_car 데이터베이스 연결 성공!")
except Exception as e:
    print(f"❌ busan_car 데이터베이스 연결 실패: {e}")

try:
    with web_engine.connect() as conn:
        print("✅ web 데이터베이스 연결 성공!")
except Exception as e:
    print(f"❌ web 데이터베이스 연결 실패: {e}")
```

## 5. Web DB 테이블 초기화

web 데이터베이스에 테이블을 생성하세요:

```bash
cd backend
python init_web_db.py
```

## 6. 서버 실행

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 문제 해결

### 연결 오류가 발생하는 경우

1. **MariaDB 서비스가 실행 중인지 확인**
   ```bash
   # Windows
   Get-Service -Name "*mysql*"
   ```

2. **포트 확인**
   ```bash
   # Windows
   netstat -an | findstr :3306
   ```

3. **방화벽 확인**
   - 로컬 연결이므로 방화벽 문제는 거의 없지만, 확인해보세요

4. **사용자 권한 확인**
   ```sql
   -- MariaDB에서 실행
   SELECT user, host FROM mysql.user WHERE user='root';
   GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'your_password';
   FLUSH PRIVILEGES;
   ```

5. **비밀번호 특수문자 문제**
   - 비밀번호에 `@`, `#`, `%` 등의 특수문자가 있으면 URL 인코딩 필요
   - 예: `password@123` → `password%40123`


