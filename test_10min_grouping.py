# 10분 단위 그룹화 테스트

# 데이터: (app_rapid_acc, app_rapid_deacc, dt)
data = [
    (3, 3, "2025-11-14 05:55:38.000"),
    (2, 3, "2025-11-14 05:56:38.000"),
    (4, 6, "2025-11-14 05:57:38.000"),
    (2, 4, "2025-11-14 05:58:38.000"),
    (0, 0, "2025-11-14 05:59:38.000"),
    (3, 4, "2025-11-14 06:00:38.000"),
    (2, 4, "2025-11-14 06:01:38.000"),
    (3, 3, "2025-11-14 06:02:38.000"),
    (1, 2, "2025-11-14 06:03:38.000"),
    (2, 4, "2025-11-14 06:04:38.000"),
    (2, 2, "2025-11-14 06:05:38.000"),
    (0, 2, "2025-11-14 06:06:38.000"),
    (3, 4, "2025-11-14 06:07:38.000"),
    (0, 0, "2025-11-14 06:08:38.000"),
    (1, 3, "2025-11-14 06:09:38.000"),
    (5, 6, "2025-11-14 06:10:38.000"),
    (5, 7, "2025-11-14 06:11:38.000"),
    (7, 9, "2025-11-14 06:12:38.000"),
    (6, 7, "2025-11-14 06:13:38.000"),
    (6, 7, "2025-11-14 06:14:38.000"),
]

from datetime import datetime
from collections import defaultdict

# 10분 단위로 그룹화
groups = defaultdict(lambda: {"acc": 0, "deacc": 0, "records": []})

for acc, deacc, dt_str in data:
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    # 10분 단위 그룹 키 (분을 10으로 나눈 몫)
    minute_group = dt.minute // 10
    group_key = (dt.year, dt.month, dt.day, dt.hour, minute_group)
    
    groups[group_key]["acc"] += acc
    groups[group_key]["deacc"] += deacc
    groups[group_key]["records"].append((dt.strftime("%H:%M"), acc, deacc))

# 결과 출력
print("=" * 80)
print("10분 단위 그룹별 급가속/급감속 합계")
print("=" * 80)
print()

total_acc = 0
total_deacc = 0
total_sum = 0

for group_key in sorted(groups.keys()):
    year, month, day, hour, minute_group = group_key
    group_data = groups[group_key]
    
    start_min = minute_group * 10
    end_min = (minute_group + 1) * 10
    
    group_sum = group_data["acc"] + group_data["deacc"]
    total_acc += group_data["acc"]
    total_deacc += group_data["deacc"]
    total_sum += group_sum
    
    print(f"그룹: {year}-{month:02d}-{day:02d} {hour:02d}:{start_min:02d}~{hour:02d}:{end_min:02d}")
    print(f"  레코드 수: {len(group_data['records'])}")
    print(f"  급가속 합계: {group_data['acc']}")
    print(f"  급감속 합계: {group_data['deacc']}")
    print(f"  그룹 합계: {group_sum}")
    print(f"  상세 레코드:")
    for time_str, acc, deacc in group_data["records"]:
        print(f"    {time_str} - 급가속: {acc}, 급감속: {deacc}")
    print()

print("=" * 80)
print("총 합계")
print("=" * 80)
print(f"총 급가속 합계: {total_acc}")
print(f"총 급감속 합계: {total_deacc}")
print(f"총 합계 (급가속 + 급감속): {total_sum}")
print(f"총 감점: {total_sum}점")

