# 안전점수 계산 로직 비교 (백엔드 vs PowerBI DAX)

## 백엔드 계산 로직 (`backend/app/api/user_safety.py`)

### 1. 졸음 감점 (`calculate_drowsy_penalty`)
```python
def calculate_drowsy_penalty(duration_sec: int) -> int:
    if duration_sec < 4:
        return 0
    penalty = duration_sec // 4  # 4초당 1점
    return min(penalty, 10)  # 최대 10점
```
- **계산 방식**: `duration_sec // 4` (4초당 1점, 정수 나눗셈)
- **최대 제한**: 10점 (40초 이상)

### 2. 급가속/급감속 감점 (`calculate_rapid_penalty`)
```python
def calculate_rapid_penalty(total_count: int) -> int:
    if total_count < 1:
        return 0
    return total_count  # 1 이상부터 1점씩 누적
```
- **계산 방식**: 10분 단위로 그룹화 → 각 그룹의 급가속+급감속 합계를 감점
- **예시**: 
  - 10분 그룹 1: 급가속 2회 + 급감속 1회 = 3점 감점
  - 10분 그룹 2: 급가속 1회 + 급감속 0회 = 1점 감점
  - 총 감점: 4점

### 3. 최종 점수
```python
total_penalty = drowsy_penalty + rapid_penalty
safety_score = max(0, 100 - total_penalty)
```

---

## PowerBI DAX 공식 (현재)

```dax
VAR no = 100
VAR deacc = CALCULATE(SUM(driving_session_info[app_rapid_deacc]))
VAR acc = CALCULATE(SUM(driving_session_info[app_rapid_acc]))
VAR drowsy = SUMX(drowsy_drive, drowsy_drive[duration_sec]/4)
VAR score = no - deacc - acc - drowsy
RETURN MAX(score, 0)
```

---

## 차이점 분석

### ❌ 문제점 1: 급가속/급감속 계산 방식이 다름

**백엔드**:
- 10분 단위로 그룹화
- 각 그룹의 급가속+급감속 합계를 감점
- 예: 급가속 5회, 급감속 3회가 같은 10분 그룹에 있으면 → 8점 감점

**PowerBI (현재)**:
- 단순 합계 사용
- 급가속 합계 + 급감속 합계를 직접 감점
- 예: 급가속 5회, 급감속 3회 → 8점 감점 (같은 그룹이든 아니든 상관없음)

### ✅ 일치: 졸음 계산
- 둘 다 `duration_sec / 4` 사용 (백엔드는 정수 나눗셈 `//`, PowerBI는 소수점 가능)

---

## 수정된 PowerBI DAX 공식 (백엔드와 일치)

```dax
session_score = 
VAR no = 100

// 졸음 감점 (각 drowsy_drive 레코드별로 duration_sec/4 계산, 최대 10점)
VAR drowsy = 
    SUMX(
        drowsy_drive,
        MIN(drowsy_drive[duration_sec] / 4, 10)  // 최대 10점 제한
    )

// 급가속/급감속 감점 (10분 단위로 그룹화 필요)
// 주의: PowerBI에서는 10분 단위 그룹화가 복잡하므로, 
// 백엔드와 동일하게 하려면 추가 계산이 필요합니다.

// 임시 해결책: 단순 합계 사용 (백엔드와 다를 수 있음)
VAR deacc = CALCULATE(SUM(driving_session_info[app_rapid_deacc]))
VAR acc = CALCULATE(SUM(driving_session_info[app_rapid_acc]))

// 또는 백엔드와 동일하게 하려면:
// 10분 단위로 그룹화하여 계산해야 하지만, PowerBI에서는 복잡함
// 대신 백엔드 API를 사용하거나, 백엔드 로직을 PowerBI에 맞춰 수정 필요

VAR score = no - deacc - acc - drowsy
RETURN MAX(score, 0)
```

---

## 권장 사항

### 옵션 1: PowerBI를 백엔드와 동일하게 수정 (복잡함)
- 10분 단위 그룹화를 PowerBI에서 구현해야 함
- DAX가 복잡해짐

### 옵션 2: 백엔드를 PowerBI와 동일하게 수정 (간단함)
- 10분 단위 그룹화 제거
- 단순 합계 사용: `rapid_penalty = SUM(app_rapid_acc) + SUM(app_rapid_deacc)`

### 옵션 3: PowerBI에서 백엔드 API 사용
- PowerBI에서 백엔드 API를 호출하여 점수 가져오기

---

## 현재 PowerBI DAX의 문제점

1. **급가속/급감속**: 백엔드는 10분 단위 그룹화를 사용하지만, PowerBI는 단순 합계
2. **졸음 최대 제한**: 백엔드는 10점 제한이 있지만, PowerBI에는 없음 (추가 필요)



