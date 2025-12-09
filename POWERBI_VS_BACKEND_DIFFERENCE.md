# PowerBI DAX vs 백엔드 계산 차이점 분석

## PowerBI DAX 공식
```dax
session_score = 
VAR no = 100
VAR deacc = CALCULATE(SUM(driving_session_info[app_rapid_deacc]))
VAR acc = CALCULATE(SUM(driving_session_info[app_rapid_acc]))
VAR drowsy = CALCULATE(SUMX(drowsy_drive, drowsy_drive[duration_sec]/4))
VAR score = no - deacc - acc - drowsy
RETURN MAX(score, 0)
```

## 백엔드 계산 로직
```python
# 1. 졸음 감점
drowsy_penalty = 0
for drowsy in drowsy_records:
    drowsy_penalty += calculate_drowsy_penalty(drowsy.duration_sec or 0)
    # calculate_drowsy_penalty: duration_sec // 4 (정수 나눗셈), 최대 10점

# 2. 급가속/급감속 감점 (10분 단위 그룹화)
rapid_penalty = 0
for info in session_infos:
    if info.dt:  # dt가 NULL이 아닌 것만
        # 10분 단위로 그룹화
        # 각 그룹의 app_rapid_acc + app_rapid_deacc 합계를 rapid_penalty에 누적

# 3. 최종 점수
safety_score = max(0, 100 - (drowsy_penalty + rapid_penalty))
```

## 차이점 분석

### 1. 급가속/급감속 계산

**백엔드**:
- `dt` 기준으로 10분 단위 그룹화
- 각 그룹의 `app_rapid_acc` + `app_rapid_deacc` 합계를 `rapid_penalty`에 누적
- `dt`가 NULL인 레코드는 제외

**PowerBI**:
- 단순 `SUM()` - 모든 레코드의 합계
- 필터 컨텍스트에 따라 데이터 범위가 다를 수 있음
- `dt`가 NULL인 레코드도 포함될 수 있음

**차이 발생 가능성**:
- `dt`가 NULL인 레코드가 있으면 백엔드는 제외하지만 PowerBI는 포함
- 10분 그룹화는 합계에 영향 없음 (각 그룹 합계를 더하면 전체 합계와 동일)

### 2. 졸음 계산 (가장 큰 차이!)

**백엔드**:
```python
penalty = duration_sec // 4  # 정수 나눗셈
return min(penalty, 10)  # 최대 10점 제한
```
- `duration_sec // 4`: 정수 나눗셈 (소수점 버림)
- 예: 7초 → 1점, 8초 → 2점, 15초 → 3점
- 최대 10점 제한 (40초 이상도 10점)

**PowerBI**:
```dax
SUMX(drowsy_drive, drowsy_drive[duration_sec]/4)
```
- `duration_sec / 4`: 소수점 나눗셈
- 예: 7초 → 1.75점, 8초 → 2점, 15초 → 3.75점
- 제한 없음 (40초 이상도 계속 증가)

**차이 예시**:
- 레코드 1: duration_sec = 7초
  - 백엔드: 1점
  - PowerBI: 1.75점
- 레코드 2: duration_sec = 15초
  - 백엔드: 3점
  - PowerBI: 3.75점
- 레코드 3: duration_sec = 50초
  - 백엔드: 10점 (최대 제한)
  - PowerBI: 12.5점

### 3. 데이터 필터링

**백엔드**:
- 특정 `session_id`에 대해 계산
- `dt`가 NULL이 아닌 레코드만 사용

**PowerBI**:
- PowerBI의 필터 컨텍스트에 따라 데이터 범위가 다름
- 같은 세션이 아닐 수 있음
- `dt` 필터링이 없을 수 있음

## 해결 방안

### 옵션 1: PowerBI를 백엔드와 동일하게 수정 (권장)

```dax
session_score = 
VAR no = 100

// 급가속/급감속: dt가 NULL이 아닌 것만, 단순 합계
VAR deacc = 
    CALCULATE(
        SUM(driving_session_info[app_rapid_deacc]),
        NOT(ISBLANK(driving_session_info[dt]))  // dt가 NULL이 아닌 것만
    )
VAR acc = 
    CALCULATE(
        SUM(driving_session_info[app_rapid_acc]),
        NOT(ISBLANK(driving_session_info[dt]))  // dt가 NULL이 아닌 것만
    )

// 졸음: 정수 나눗셈, 최대 10점 제한
VAR drowsy = 
    SUMX(
        drowsy_drive,
        MIN(FLOOR(drowsy_drive[duration_sec] / 4, 1), 10)  // 정수 나눗셈, 최대 10점
    )

VAR score = no - deacc - acc - drowsy
RETURN MAX(score, 0)
```

### 옵션 2: 백엔드를 PowerBI와 동일하게 수정

- 졸음 계산에서 최대 제한 제거
- 소수점 사용 (하지만 점수는 정수로 반올림)

## 결론

**가장 큰 차이는 졸음 계산**입니다:
1. 백엔드는 정수 나눗셈 + 최대 10점 제한
2. PowerBI는 소수점 나눗셈 + 제한 없음

이 차이로 인해 점수가 다를 수 있습니다.



