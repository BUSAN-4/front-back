# 안전점수 차이 원인 분석

## 문제 상황
- 백엔드: 2025년 12월 평균 안전운전 점수 (47개 세션)
- PowerBI: 동일 기간 평균 점수가 다름

## 핵심 차이점 발견

### 백엔드 로직 (user_safety.py)

```python
# 급가속/급감속 카운트 (각 info_id별로 카운트)
# app_rapid_acc과 app_rapid_deacc의 값이 1 이상이면 카운트
if info.app_rapid_acc and info.app_rapid_acc > 0:
    current_group_rapid_count += 1  # 1씩 증가
if info.app_rapid_deacc and info.app_rapid_deacc > 0:
    current_group_rapid_count += 1  # 1씩 증가
```

**백엔드 방식**:
- `app_rapid_acc > 0`이면 **카운트를 1씩 증가** (각 info_id별로)
- `app_rapid_deacc > 0`이면 **카운트를 1씩 증가** (각 info_id별로)
- 즉, **발생 횟수**를 카운트

### PowerBI DAX

```dax
VAR deacc = CALCULATE(SUM(driving_session_info[app_rapid_deacc]))
VAR acc = CALCULATE(SUM(driving_session_info[app_rapid_acc]))
```

**PowerBI 방식**:
- `app_rapid_deacc`의 **실제 값의 합계**
- `app_rapid_acc`의 **실제 값의 합계**
- 즉, **값의 합계**를 사용

## 차이가 나는 경우

### 시나리오 1: app_rapid_acc 값이 1이 아닌 경우
만약 `app_rapid_acc` 값이 2, 3, 4 같은 값이라면:

**백엔드**:
- `app_rapid_acc = 2` → 카운트 1 증가
- `app_rapid_acc = 3` → 카운트 1 증가
- 총 감점: 2점

**PowerBI**:
- `app_rapid_acc = 2` → 합계에 2 추가
- `app_rapid_acc = 3` → 합계에 3 추가
- 총 감점: 5점

### 시나리오 2: app_rapid_acc 값이 모두 1인 경우
만약 모든 `app_rapid_acc` 값이 1이라면:

**백엔드**:
- 각 info_id별로 1씩 카운트
- 총 감점: 발생 횟수

**PowerBI**:
- 각 값의 합계
- 총 감점: 발생 횟수 (값이 모두 1이면 동일)

## 해결 방안

### 옵션 1: PowerBI를 백엔드와 동일하게 수정 (권장)

```dax
session_score = 
VAR no = 100

// 급가속/급감속: 값이 0보다 크면 1로 카운트 (백엔드와 동일)
VAR deacc = 
    SUMX(
        driving_session_info,
        IF(driving_session_info[app_rapid_deacc] > 0, 1, 0)
    )
VAR acc = 
    SUMX(
        driving_session_info,
        IF(driving_session_info[app_rapid_acc] > 0, 1, 0)
    )

// 졸음 감점
VAR drowsy = SUMX(drowsy_drive, drowsy_drive[duration_sec] / 4)

VAR score = no - deacc - acc - drowsy
RETURN MAX(score, 0)
```

**주의**: 이 방식도 10분 단위 그룹화는 없지만, 백엔드의 카운트 방식과는 일치합니다.

### 옵션 2: 백엔드를 PowerBI와 동일하게 수정

백엔드에서 실제 값을 합산하도록 수정:
```python
if info.app_rapid_acc and info.app_rapid_acc > 0:
    current_group_rapid_count += info.app_rapid_acc  # 값 자체를 더함
if info.app_rapid_deacc and info.app_rapid_deacc > 0:
    current_group_rapid_count += info.app_rapid_deacc  # 값 자체를 더함
```

### 옵션 3: 10분 그룹화도 PowerBI에 구현 (복잡)

PowerBI에서 10분 단위 그룹화를 구현하려면 더 복잡한 DAX가 필요합니다.

## 확인 필요 사항

1. **`app_rapid_acc`와 `app_rapid_deacc`의 실제 값 범위**
   - 모두 1인가? 아니면 2, 3, 4 같은 값도 있는가?

2. **데이터 샘플 확인**
   ```sql
   SELECT 
       session_id,
       app_rapid_acc,
       app_rapid_deacc,
       COUNT(*) as count
   FROM driving_session_info
   WHERE app_rapid_acc > 0 OR app_rapid_deacc > 0
   GROUP BY session_id, app_rapid_acc, app_rapid_deacc
   LIMIT 20;
   ```

## 권장 사항

**옵션 1을 권장합니다** (PowerBI를 백엔드와 동일하게 수정)
- 백엔드 로직이 이미 구현되어 있고 작동 중
- PowerBI만 수정하면 됨
- 10분 그룹화는 제외하더라도 카운트 방식은 일치시킬 수 있음



