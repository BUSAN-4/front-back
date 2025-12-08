# Web DB 설정 가이드

## 데이터베이스 구조

이 프로젝트는 두 개의 데이터베이스를 사용합니다:

1. **busan_car** (읽기 전용)
   - 기존 데이터 조회용
   - `DATABASE_URL` 환경 변수로 설정

2. **web** (쓰기용)
   - 웹 애플리케이션에서 생성/수정/삭제하는 모든 데이터 저장
   - `WEB_DATABASE_URL` 환경 변수로 설정

## 환경 변수 설정

`.env` 파일에 다음 변수를 추가하세요:

```env
# busan_car 데이터베이스 (읽기 전용)
DATABASE_URL=mysql+pymysql://user:password@host:port/busan_car?charset=utf8mb4

# web 데이터베이스 (쓰기용)
WEB_DATABASE_URL=mysql+pymysql://user:password@host:port/web?charset=utf8mb4
```

## Web DB 테이블 초기화

web 데이터베이스에 테이블을 생성하려면 다음 명령을 실행하세요:

```bash
cd backend
python init_web_db.py
```

이 스크립트는 다음 테이블을 생성합니다:
- `users`: 사용자 정보
- `user_vehicle_mapping`: 사용자-차량 매핑

## 사용자-차량 매핑

일반 사용자가 자신의 안전운전 점수를 조회하려면 먼저 차량을 등록해야 합니다.
`user_vehicle_mapping` 테이블에 사용자 ID와 차량 ID(car_id)를 매핑하여 저장합니다.

## API 엔드포인트

### 일반 사용자 안전운전 점수

- `GET /api/user/safety-score/monthly?year={year}&month={month}`
  - 월별 안전운전 점수 조회 (session_id별)
  - 인증 필요 (일반 사용자만)

- `GET /api/user/safety-score/session/{session_id}`
  - 세션별 안전운전 점수 상세 조회
  - 인증 필요 (일반 사용자만)

## 점수 계산 로직

### 졸음운전 감점
- 5초 이상: 감점 1점
- 10초 이상: 감점 2점
- 50초 이상: 감점 10점

### 급가속/급감속 감점
- 10분 단위로 그룹화
- session_id별 info_id를 매칭
- app_rapid_acc + app_rapid_deacc 총계가 2 이상이면 감점 시작
- 총합 7번이면 감점 6점 (2 이상부터 카운트)

### 최종 점수
- 기본 점수: 100점
- 총 감점 = 졸음운전 감점 + 급가속/급감속 감점
- 안전 점수 = max(0, 100 - 총 감점)





