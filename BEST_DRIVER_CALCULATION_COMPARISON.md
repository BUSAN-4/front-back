# 베스트 드라이버 계산 방식 비교

## 현재 방식 (발생률 기반)

### 계산 로직
```python
# 1. 월별 합계 계산
total_rapid_acc = SUM(app_rapid_acc)  # 해당 월의 모든 급가속 합계
total_rapid_deacc = SUM(app_rapid_deacc)  # 해당 월의 모든 급감속 합계
total_gaze_closure = SUM(gaze_closure)  # 해당 월의 모든 눈감음 합계

# 2. 발생률 계산
incident_rate = (total_rapid_acc + total_rapid_deacc + total_gaze_closure) / session_count

# 3. 점수 계산 (1000점 만점)
driver_score = 1000 - (incident_rate * 1000)
```

### 특징
- **1000점 만점**
- **발생률 기반**: 세션당 평균 사고 횟수
- **공정성**: 세션 수가 다른 드라이버들을 공정하게 비교
- **정렬**: 발생률 오름차순 (낮을수록 좋음)

---

## 안전운전 점수 방식 (일반 사용자 대시보드)

### 계산 로직
```python
# 각 세션별로 계산
for session in sessions:
    # 1. 졸음 감점
    drowsy_penalty = 0
    for drowsy in drowsy_records:
        drowsy_penalty += calculate_drowsy_penalty(drowsy.duration_sec)  # duration_sec // 4, 최대 10점
    
    # 2. 급가속/급감속 감점 (10분 단위 그룹화)
    rapid_penalty = 0
    # 10분 단위로 그룹화하여 각 그룹의 app_rapid_acc + app_rapid_deacc 합계를 rapid_penalty에 누적
    
    # 3. 세션별 안전 점수
    safety_score = max(0, 100 - (drowsy_penalty + rapid_penalty))

# 4. 월별 평균 점수
average_score = sum(safety_scores) / len(safety_scores)
```

### 특징
- **100점 만점**
- **감점 방식**: 100점에서 감점
- **10분 단위 그룹화**: 급가속/급감속을 10분 단위로 그룹화
- **세션별 계산 후 평균**: 각 세션의 점수를 계산한 후 평균

---

## 차이점

| 항목 | 현재 방식 (발생률) | 안전운전 점수 방식 |
|------|-------------------|-------------------|
| 점수 체계 | 1000점 만점 | 100점 만점 |
| 계산 방식 | 발생률 기반 | 감점 방식 |
| 급가속/급감속 | 단순 합계 | 10분 단위 그룹화 |
| 졸음 계산 | gaze_closure 합계 | duration_sec // 4, 최대 10점 |
| 정렬 기준 | 발생률 오름차순 | 평균 점수 내림차순 |

---

## 선택 사항

### 옵션 1: 현재 방식 유지 (발생률 기반)
- 장점: 공정한 비교 (세션 수 고려)
- 단점: 일반 사용자 대시보드와 다른 점수 체계

### 옵션 2: 안전운전 점수 방식으로 변경
- 장점: 일반 사용자 대시보드와 동일한 점수 체계
- 단점: 계산이 복잡함 (각 세션별로 계산 후 평균)

---

## 권장 사항

**현재 방식을 유지하는 것을 권장합니다.**

이유:
1. **공정성**: 세션 수가 다른 드라이버들을 공정하게 비교
2. **명확성**: 발생률이 직관적 (세션당 평균 사고 횟수)
3. **성능**: 단순 합계 계산이 빠름

하지만 사용자가 원한다면 안전운전 점수 방식으로 변경 가능합니다.



