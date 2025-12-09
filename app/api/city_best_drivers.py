"""
베스트 드라이버 계산 유틸리티 함수
일반 사용자 안전운전 점수 계산 방식과 동일하게 계산
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, or_, and_
from datetime import datetime
from app.models.busan_car_models import (
    BusanCarDrivingSession,
    BusanCarDrivingSessionInfo,
    BusanCarDrowsyDrive
)


def calculate_drowsy_penalty(duration_sec: int) -> int:
    """
    졸음운전 감점 계산
    - 5초 이상: 감점 1점
    - 10초 이상: 감점 2점
    - 50초 이상: 감점 10점
    """
    if duration_sec < 5:
        return 0
    elif duration_sec < 10:
        return 1
    elif duration_sec < 50:
        return 2
    else:
        return 10


def calculate_session_safety_score(
    db: Session,
    session_id: str
) -> dict:
    """
    세션별 안전운전 점수 계산 (일반 사용자와 동일한 방식)
    
    Returns:
        dict: {
            "safetyScore": 점수 (0-100),
            "drowsyPenalty": 졸음 감점,
            "rapidPenalty": 급가속/급감속 감점,
            "totalPenalty": 총 감점,
            "totalRapidAcc": 급가속 총합,
            "totalRapidDeacc": 급감속 총합,
            "totalGazeClosure": 눈 감음 총합
        }
    """
    # 졸음운전 데이터 조회
    drowsy_records = db.query(BusanCarDrowsyDrive).filter(
        BusanCarDrowsyDrive.session_id == session_id
    ).all()
    
    # 졸음운전 감점 계산 및 gaze_closure 합계
    drowsy_penalty = 0
    total_gaze_closure = 0
    for drowsy in drowsy_records:
        drowsy_penalty += calculate_drowsy_penalty(drowsy.duration_sec or 0)
        total_gaze_closure += drowsy.gaze_closure or 0
    
    # 급가속/급감속 데이터 조회 (createdDate 기준 10분 단위로 그룹화)
    session_infos = db.query(BusanCarDrivingSessionInfo).filter(
        BusanCarDrivingSessionInfo.session_id == session_id,
        BusanCarDrivingSessionInfo.createdDate.isnot(None)
    ).order_by(BusanCarDrivingSessionInfo.createdDate).all()
    
    # 10분 단위로 그룹화하여 급가속/급감속 합계 계산
    rapid_penalty = 0
    total_rapid_acc = 0  # 전체 급가속 합계
    total_rapid_deacc = 0  # 전체 급감속 합계
    current_10min_group = None
    current_group_acc_sum = 0
    current_group_deacc_sum = 0
    
    for info in session_infos:
        if info.createdDate:
            # 10분 단위로 그룹화
            minute_group = info.createdDate.minute // 10
            group_key = (
                info.createdDate.year,
                info.createdDate.month,
                info.createdDate.day,
                info.createdDate.hour,
                minute_group
            )
            
            if current_10min_group != group_key:
                # 새로운 10분 그룹 시작
                if current_10min_group is not None:
                    # 이전 그룹의 총합(급가속 + 급감속)을 총 감점에 추가
                    group_total = current_group_acc_sum + current_group_deacc_sum
                    rapid_penalty += group_total
                current_10min_group = group_key
                current_group_acc_sum = 0
                current_group_deacc_sum = 0
            
            # 급가속/급감속 합계 계산 (전체 합계도 누적)
            if info.app_rapid_acc:
                current_group_acc_sum += info.app_rapid_acc
                total_rapid_acc += info.app_rapid_acc
            if info.app_rapid_deacc:
                current_group_deacc_sum += info.app_rapid_deacc
                total_rapid_deacc += info.app_rapid_deacc
    
    # 마지막 그룹의 총합을 총 감점에 추가
    if current_10min_group is not None:
        group_total = current_group_acc_sum + current_group_deacc_sum
        rapid_penalty += group_total
    
    # 총 감점
    total_penalty = drowsy_penalty + rapid_penalty
    
    # 안전 점수 (100점 만점에서 감점)
    safety_score = max(0, 100 - total_penalty)
    
    return {
        "safetyScore": safety_score,
        "drowsyPenalty": drowsy_penalty,
        "rapidPenalty": rapid_penalty,
        "totalPenalty": total_penalty,
        "totalRapidAcc": total_rapid_acc,
        "totalRapidDeacc": total_rapid_deacc,
        "totalGazeClosure": total_gaze_closure
    }

