"""
일반 사용자 안전운전 점수 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from typing import List, Optional
from datetime import datetime
from app.database import get_busan_car_db, get_web_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.busan_car_models import (
    BusanCarDrivingSession,
    BusanCarDrivingSessionInfo,
    BusanCarDrowsyDrive,
    BusanCarUserVehicle
)

router = APIRouter()


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


def calculate_rapid_penalty(total_count: int) -> int:
    """
    급가속/급감속 감점 계산
    - 총계가 1 이상이면 감점 1점 누적
    - 총합 7번이면 감점 7점
    """
    if total_count < 1:
        return 0
    return total_count  # 1 이상부터 1점씩 누적


@router.get("/safety-score/monthly", response_model=List[dict])
async def get_monthly_safety_scores(
    year: int = Query(..., description="연도"),
    month: int = Query(..., description="월 (1-12)"),
    current_user: User = Depends(get_current_active_user),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    월별 안전운전 점수 조회 (session_id별)
    end_time의 년도와 월별로 집계
    """
    if current_user.role.value != "GENERAL":
        raise HTTPException(status_code=403, detail="일반 사용자만 접근 가능합니다")
    
    # 사용자의 차량 조회 (vehicles 테이블에서)
    user_vehicles = web_db.query(Vehicle).filter(
        Vehicle.user_id == current_user.id
    ).all()
    
    if not user_vehicles:
        return []  # 등록된 차량이 없으면 빈 리스트 반환
    
    # vehicles 테이블에서 car_id 추출 (이미 매핑되어 있음)
    car_ids = [v.car_id for v in user_vehicles if v.car_id]
    
    if not car_ids:
        return []  # car_id가 매핑되지 않은 차량만 있으면 빈 리스트 반환
    
    # car_id와 license_plate 매핑 딕셔너리 생성
    car_id_to_plate = {v.car_id: v.license_plate for v in user_vehicles if v.car_id}
    
    # 해당 월의 세션 조회 (created_at 기준, 사용자의 차량만)
    # created_at이 없으면 start_time 기준으로 조회
    sessions = busan_car_db.query(BusanCarDrivingSession).filter(
        BusanCarDrivingSession.car_id.in_(car_ids),
        or_(
            and_(
                extract('year', BusanCarDrivingSession.created_at) == year,
                extract('month', BusanCarDrivingSession.created_at) == month
            ),
            and_(
                BusanCarDrivingSession.created_at.is_(None),
                extract('year', BusanCarDrivingSession.start_time) == year,
                extract('month', BusanCarDrivingSession.start_time) == month
            )
        )
    ).all()
    
    results = []
    
    for session in sessions:
        session_id = session.session_id
        car_id = session.car_id
        license_plate = car_id_to_plate.get(car_id, "Unknown")
        
        # 졸음운전 데이터 조회
        drowsy_records = busan_car_db.query(BusanCarDrowsyDrive).filter(
            BusanCarDrowsyDrive.session_id == session_id
        ).all()
        
        # 졸음운전 감점 계산
        drowsy_penalty = 0
        gaze_closure_count = 0
        head_drop_count = 0
        yawn_flag_count = 0
        
        for drowsy in drowsy_records:
            drowsy_penalty += calculate_drowsy_penalty(drowsy.duration_sec or 0)
            gaze_closure_count += drowsy.gaze_closure or 0
            head_drop_count += drowsy.head_drop or 0
            yawn_flag_count += drowsy.yawn_flag or 0
        
        # 급가속/급감속 데이터 조회 (10분 단위로 그룹화)
        # session_id별 info_id를 매칭하여 createdDate가 10분 단위로 그룹화
        session_infos = busan_car_db.query(BusanCarDrivingSessionInfo).filter(
            BusanCarDrivingSessionInfo.session_id == session_id,
            BusanCarDrivingSessionInfo.createdDate.isnot(None)
        ).order_by(BusanCarDrivingSessionInfo.createdDate).all()
        
        # 10분 단위로 그룹화하여 급가속/급감속 합계 계산
        rapid_penalty = 0
        current_10min_group = None
        current_group_acc_sum = 0  # 현재 그룹의 급가속 합계
        current_group_deacc_sum = 0  # 현재 그룹의 급감속 합계
        
        for info in session_infos:
            if info.createdDate:
                # 10분 단위로 그룹화 (분을 10으로 나눈 몫)
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
                
                # 급가속/급감속 합계 계산 (각 10분 그룹 내에서 실제 값의 합계)
                if info.app_rapid_acc:
                    current_group_acc_sum += info.app_rapid_acc
                if info.app_rapid_deacc:
                    current_group_deacc_sum += info.app_rapid_deacc
        
        # 마지막 그룹의 총합을 총 감점에 추가
        if current_10min_group is not None:
            group_total = current_group_acc_sum + current_group_deacc_sum
            rapid_penalty += group_total
        
        # 총 감점
        total_penalty = drowsy_penalty + rapid_penalty
        
        # 안전 점수 (100점 만점에서 감점)
        safety_score = max(0, 100 - total_penalty)
        
        results.append({
            "sessionId": session_id,
            "carId": session.car_id,
            "licensePlate": license_plate,
            "startTime": session.start_time.isoformat() if session.start_time else None,
            "endTime": session.end_time.isoformat() if session.end_time else None,
            "safetyScore": safety_score,
            "totalPenalty": total_penalty,
            "drowsyPenalty": drowsy_penalty,
            "rapidPenalty": rapid_penalty,
            "gazeClosureCount": gaze_closure_count,
            "headDropCount": head_drop_count,
            "yawnFlagCount": yawn_flag_count
        })
    
    return results


@router.get("/safety-score/session/{session_id}", response_model=dict)
async def get_session_safety_detail(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    세션별 안전운전 점수 상세 조회
    """
    if current_user.role.value != "GENERAL":
        raise HTTPException(status_code=403, detail="일반 사용자만 접근 가능합니다")
    
    # 세션 조회
    session = busan_car_db.query(BusanCarDrivingSession).filter(
        BusanCarDrivingSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    
    car_id = session.car_id
    
    # 사용자의 차량인지 확인 (vehicles 테이블에서 car_id로 확인)
    user_vehicle = web_db.query(Vehicle).filter(
        Vehicle.user_id == current_user.id,
        Vehicle.car_id == car_id
    ).first()
    
    if not user_vehicle:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다")
    
    license_plate = user_vehicle.license_plate
    
    # 졸음운전 데이터 조회
    drowsy_records = busan_car_db.query(BusanCarDrowsyDrive).filter(
        BusanCarDrowsyDrive.session_id == session_id
    ).all()
    
    # 졸음운전 감점 계산
    drowsy_penalty = 0
    gaze_closure_count = 0
    head_drop_count = 0
    yawn_flag_count = 0
    drowsy_details = []
    
    for drowsy in drowsy_records:
        penalty = calculate_drowsy_penalty(drowsy.duration_sec or 0)
        drowsy_penalty += penalty
        gaze_closure_count += drowsy.gaze_closure or 0
        head_drop_count += drowsy.head_drop or 0
        yawn_flag_count += drowsy.yawn_flag or 0
        
        drowsy_details.append({
            "drowsyId": drowsy.drowsy_id,
            "detectedAt": drowsy.detected_at.isoformat() if drowsy.detected_at else None,
            "durationSec": drowsy.duration_sec,
            "penalty": penalty,
            "gazeClosure": drowsy.gaze_closure,
            "headDrop": drowsy.head_drop,
            "yawnFlag": drowsy.yawn_flag
        })
    
    # 급가속/급감속 데이터 조회 (10분 단위로 그룹화)
    # session_id별 info_id를 매칭하여 createdDate가 10분 단위로 그룹화
    session_infos = busan_car_db.query(BusanCarDrivingSessionInfo).filter(
        BusanCarDrivingSessionInfo.session_id == session_id,
        BusanCarDrivingSessionInfo.createdDate.isnot(None)
    ).order_by(BusanCarDrivingSessionInfo.createdDate).all()
    
    # 10분 단위로 그룹화하여 급가속/급감속 합계 계산
    rapid_penalty = 0
    current_10min_group = None
    current_group_acc_sum = 0  # 현재 그룹의 급가속 합계
    current_group_deacc_sum = 0  # 현재 그룹의 급감속 합계
    rapid_details = []
    
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
                    rapid_details.append({
                        "timeGroup": f"{current_10min_group[3]:02d}:{current_10min_group[4]*10:02d}",
                        "rapidAccSum": current_group_acc_sum,
                        "rapidDeaccSum": current_group_deacc_sum,
                        "rapidCount": group_total,
                        "penalty": group_total,
                        "infoIds": []  # 필요시 info_id 목록 추가 가능
                    })
                current_10min_group = group_key
                current_group_acc_sum = 0
                current_group_deacc_sum = 0
            
            # 급가속/급감속 합계 계산 (각 10분 그룹 내에서 실제 값의 합계)
            if info.app_rapid_acc:
                current_group_acc_sum += info.app_rapid_acc
            if info.app_rapid_deacc:
                current_group_deacc_sum += info.app_rapid_deacc
    
    # 마지막 그룹의 총합을 총 감점에 추가
    if current_10min_group is not None:
        group_total = current_group_acc_sum + current_group_deacc_sum
        rapid_penalty += group_total
        rapid_details.append({
            "timeGroup": f"{current_10min_group[3]:02d}:{current_10min_group[4]*10:02d}",
            "rapidAccSum": current_group_acc_sum,
            "rapidDeaccSum": current_group_deacc_sum,
            "rapidCount": group_total,
            "penalty": group_total
        })
    
    # 총 감점
    total_penalty = drowsy_penalty + rapid_penalty
    
    # 안전 점수 (100점 만점에서 감점)
    safety_score = max(0, 100 - total_penalty)
    
    return {
        "sessionId": session_id,
        "carId": session.car_id,
        "licensePlate": license_plate,
        "startTime": session.start_time.isoformat() if session.start_time else None,
        "endTime": session.end_time.isoformat() if session.end_time else None,
        "safetyScore": safety_score,
        "totalPenalty": total_penalty,
        "drowsyPenalty": drowsy_penalty,
        "rapidPenalty": rapid_penalty,
        "gazeClosureCount": gaze_closure_count,
        "headDropCount": head_drop_count,
        "yawnFlagCount": yawn_flag_count,
        "drowsyDetails": drowsy_details,
        "rapidDetails": rapid_details
    }

