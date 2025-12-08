from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, extract, text
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.database import get_db
from app.api.deps import require_busan_admin
from app.models.user import User
from app.models.missing_person_detection import MissingPersonDetection
from app.models.arrears_detection import ArrearsDetection
from app.models.drowsy_drive import DrowsyDrive
from app.models.driving_session import DrivingSession
from app.models.driving_session_info import DrivingSessionInfo
from app.models.user_vehicle import UserVehicle

router = APIRouter()


@router.get("/missing-person", response_model=List[dict])
async def get_missing_person_detections(
    missing_id: Optional[str] = Query(None, description="실종자 ID로 필터링"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_db)
):
    """실종자 탐지 조회 (missing_person_detection 테이블)"""
    query = db.query(MissingPersonDetection)
    
    if missing_id:
        query = query.filter(MissingPersonDetection.missing_id == missing_id)
    
    detections = query.order_by(MissingPersonDetection.detected_time.desc()).all()
    
    return [{
        "detectionId": d.detection_id,
        "imageId": d.image_id,
        "missingId": d.missing_id,
        "detectionSuccess": bool(d.detection_success),
        "detectedLat": d.detected_lat,
        "detectedLon": d.detected_lon,
        "detectedTime": d.detected_time.isoformat() if d.detected_time else None,
        "detectedAt": d.detected_at
    } for d in detections]


@router.get("/arrears", response_model=List[dict])
async def get_arrears_detections(
    car_plate_number: Optional[str] = Query(None, description="차량 번호로 필터링"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_db)
):
    """체납 차량 탐지 조회 (arrears_detection 테이블)"""
    query = db.query(ArrearsDetection)
    
    if car_plate_number:
        query = query.filter(ArrearsDetection.car_plate_number == car_plate_number)
    
    detections = query.order_by(ArrearsDetection.detected_time.desc()).all()
    
    return [{
        "detectionId": d.detection_id,
        "carPlateNumber": d.car_plate_number,
        "imageId": d.image_id,
        "detectionSuccess": bool(d.detection_success),
        "detectedLat": d.detected_lat,
        "detectedLon": d.detected_lon,
        "detectedTime": d.detected_time.isoformat() if d.detected_time else None
    } for d in detections]


@router.get("/drowsy-drive", response_model=List[dict])
async def get_drowsy_drive_detections(
    session_id: Optional[str] = Query(None, description="세션 ID로 필터링"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_db)
):
    """운전자 운전태도(졸음운전) 실시간 탐지 조회 (drowsy_drive 테이블)"""
    query = db.query(DrowsyDrive)
    
    if session_id:
        query = query.filter(DrowsyDrive.session_id == session_id)
    
    if start_date:
        query = query.filter(DrowsyDrive.detected_at >= start_date)
    
    if end_date:
        query = query.filter(DrowsyDrive.detected_at <= end_date)
    
    detections = query.order_by(DrowsyDrive.detected_at.desc()).all()
    
    return [{
        "drowsyId": d.drowsy_id,
        "sessionId": d.session_id,
        "detectedLat": d.detected_lat,
        "detectedLon": d.detected_lon,
        "detectedAt": d.detected_at.isoformat() if d.detected_at else None,
        "durationSec": d.duration_sec,
        "gazeClosure": d.gaze_closure,
        "headDrop": d.head_drop,
        "yawnFlag": d.yawn_flag,
        "abnormalFlag": d.abnormal_flag,
        "createdAt": d.created_at.isoformat() if d.created_at else None,
        "updatedAt": d.updated_at.isoformat() if d.updated_at else None
    } for d in detections]


# 안전운전관리 API 엔드포인트들
@router.get("/safe-driving/sample-car-ids", response_model=List[str])
async def get_sample_car_ids(
    limit: int = Query(10, description="샘플 개수"),
    db: Session = Depends(get_db)
):
    """실제 DB에 있는 car_id 샘플 조회 (디버깅용)"""
    car_ids = db.query(UserVehicle.car_id).limit(limit).all()
    return [row.car_id for row in car_ids if row.car_id]


@router.get("/safe-driving/stats", response_model=dict)
async def get_safe_driving_stats(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_db)
):
    """안전운전 주요 지표 조회 (주행 차량 수, 전체 안전운전율)"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    # 현재 주행 중인 차량 수 (end_time이 NULL이거나 미래인 세션)
    active_sessions = db.query(DrivingSession).filter(
        or_(
            DrivingSession.end_time.is_(None),
            DrivingSession.end_time > now
        )
    ).count()
    
    # 해당 월의 전체 세션 수
    month_sessions = db.query(DrivingSession).filter(
        extract('year', DrivingSession.start_time) == target_year,
        extract('month', DrivingSession.start_time) == target_month
    ).count()
    
    # 해당 월의 안전운전 데이터 집계
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 급가속, 급감속, 졸음운전 집계
    rapid_acc_count = db.query(func.count(DrivingSessionInfo.info_id)).join(
        DrivingSession, DrivingSessionInfo.session_id == DrivingSession.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end,
        DrivingSessionInfo.app_rapid_acc > 0
    ).scalar() or 0
    
    rapid_deacc_count = db.query(func.count(DrivingSessionInfo.info_id)).join(
        DrivingSession, DrivingSessionInfo.session_id == DrivingSession.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end,
        DrivingSessionInfo.app_rapid_deacc > 0
    ).scalar() or 0
    
    drowsy_count = db.query(func.count(DrowsyDrive.drowsy_id)).filter(
        DrowsyDrive.detected_at >= month_start,
        DrowsyDrive.detected_at < month_end,
        DrowsyDrive.abnormal_flag > 0
    ).scalar() or 0
    
    # 전체 데이터 포인트 수 (실제 driving_session_info 레코드 수)
    total_data_points = db.query(func.count(DrivingSessionInfo.info_id)).join(
        DrivingSession, DrivingSessionInfo.session_id == DrivingSession.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end
    ).scalar() or 1
    
    # 안전운전율 계산 (100 - (위험 행동 비율 * 100))
    # 위험 행동은 각각 독립적으로 발생할 수 있으므로 합산
    unsafe_ratio = (rapid_acc_count + rapid_deacc_count + drowsy_count) / total_data_points if total_data_points > 0 else 0
    safety_rate = max(0, min(100, (1 - unsafe_ratio) * 100))
    
    return {
        "activeVehicles": active_sessions,
        "totalSessions": month_sessions,
        "safetyRate": round(safety_rate, 2),
        "rapidAccelCount": rapid_acc_count,
        "rapidDecelCount": rapid_deacc_count,
        "drowsyCount": drowsy_count,
        "month": target_month,
        "year": target_year
    }


@router.get("/safe-driving/districts", response_model=List[dict])
async def get_district_safe_driving(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_db)
):
    """구별 안전운전 현황 조회"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 구별 집계 (user_location에서 구 추출)
    # user_location 형식: "부산시 해운대구" 또는 "해운대구"
    # Python에서 구 추출 후 집계 (더 정확한 처리)
    
    # 먼저 모든 데이터를 가져와서 Python에서 처리
    district_data = db.query(
        UserVehicle.user_location,
        DrivingSessionInfo.app_rapid_acc,
        DrivingSessionInfo.app_rapid_deacc,
        DrowsyDrive.abnormal_flag,
        DrivingSession.session_id
    ).join(
        DrivingSession, UserVehicle.car_id == DrivingSession.car_id
    ).join(
        DrivingSessionInfo, DrivingSession.session_id == DrivingSessionInfo.session_id
    ).outerjoin(
        DrowsyDrive, DrivingSession.session_id == DrowsyDrive.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end,
        UserVehicle.user_location.isnot(None),
        UserVehicle.user_location.like('%구%')
    ).all()
    
    # 구별로 집계
    district_dict = {}
    for row in district_data:
        # 구 추출 (user_location에서 "구"로 끝나는 부분 찾기)
        location = row.user_location or ""
        district = "기타"
        
        # "구"로 끝나는 부분 찾기
        if "구" in location:
            # 공백으로 분리 후 "구"가 포함된 부분 찾기
            parts = location.split()
            for part in parts:
                if "구" in part:
                    # "구" 앞부분 + "구" 추출
                    idx = part.find("구")
                    if idx >= 0:
                        district = part[:idx+1] if idx > 0 else part
                    break
            # 공백이 없으면 전체에서 "구" 찾기
            if district == "기타" and "구" in location:
                idx = location.find("구")
                if idx >= 0:
                    district = location[:idx+1] if idx > 0 else location
        
        if district not in district_dict:
            district_dict[district] = {
                "sessions": set(),
                "rapid_acc": 0,
                "rapid_deacc": 0,
                "drowsy": 0,
                "total_data_points": 0
            }
        
        district_dict[district]["sessions"].add(row.session_id)
        district_dict[district]["total_data_points"] += 1
        
        if row.app_rapid_acc and row.app_rapid_acc > 0:
            district_dict[district]["rapid_acc"] += 1
        if row.app_rapid_deacc and row.app_rapid_deacc > 0:
            district_dict[district]["rapid_deacc"] += 1
        if row.abnormal_flag and row.abnormal_flag > 0:
            district_dict[district]["drowsy"] += 1
    
    result = []
    for district, data in district_dict.items():
        session_count = len(data["sessions"])
        rapid_acc = data["rapid_acc"]
        rapid_deacc = data["rapid_deacc"]
        drowsy = data["drowsy"]
        total_data_points = data["total_data_points"]
        
        # 안전점수 계산 (100점 만점, 위험 행동이 적을수록 높은 점수)
        total_incidents = rapid_acc + rapid_deacc + drowsy
        if total_data_points > 0:
            safety_score = max(0, min(100, 100 - (total_incidents / total_data_points * 100)))
        else:
            safety_score = 100
        
        result.append({
            "district": district,
            "safetyScore": round(safety_score, 1),
            "rapidAccelCount": rapid_acc,
            "rapidDecelCount": rapid_deacc,
            "drowsyCount": drowsy,
            "sessionCount": session_count,
            "totalIncidents": total_incidents
        })
    
    # 안전점수 기준으로 정렬
    result.sort(key=lambda x: x['safetyScore'], reverse=True)
    
    # 순위 추가
    for i, item in enumerate(result, 1):
        item['rank'] = i
    
    return result


@router.get("/safe-driving/demographics", response_model=List[dict])
async def get_demographics_safe_driving(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_db)
):
    """성별, 연령별 운전습관 조회"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 연령대 그룹화 함수
    age_group = case(
        (and_(UserVehicle.age >= 20, UserVehicle.age < 30), '20대'),
        (and_(UserVehicle.age >= 30, UserVehicle.age < 40), '30대'),
        (and_(UserVehicle.age >= 40, UserVehicle.age < 50), '40대'),
        (UserVehicle.age >= 50, '50대 이상'),
        else_='기타'
    )
    
    demographics = db.query(
        UserVehicle.user_sex.label('gender'),
        age_group.label('age_group'),
        func.count(func.distinct(DrivingSession.session_id)).label('session_count'),
        func.count(DrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((DrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((DrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((DrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy')
    ).join(
        DrivingSession, UserVehicle.car_id == DrivingSession.car_id
    ).join(
        DrivingSessionInfo, DrivingSession.session_id == DrivingSessionInfo.session_id
    ).outerjoin(
        DrowsyDrive, DrivingSession.session_id == DrowsyDrive.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end,
        UserVehicle.user_sex.isnot(None),
        UserVehicle.age.isnot(None)
    ).group_by('gender', 'age_group').all()
    
    result = []
    for row in demographics:
        gender = row.gender or "기타"
        age_group = row.age_group or "기타"
        session_count = row.session_count or 0
        total_data_points = row.total_data_points or 1
        rapid_acc = int(row.rapid_acc or 0)
        rapid_deacc = int(row.rapid_deacc or 0)
        drowsy = int(row.drowsy or 0)
        
        total_incidents = rapid_acc + rapid_deacc + drowsy
        
        if total_data_points > 0:
            safety_score = max(0, min(100, 100 - (total_incidents / total_data_points * 100)))
        else:
            safety_score = 100
        
        result.append({
            "category": f"{age_group} {gender}",
            "ageGroup": age_group,
            "gender": gender,
            "safetyScore": round(safety_score, 1),
            "sessionCount": session_count,
            "rapidAccelCount": rapid_acc,
            "rapidDecelCount": rapid_deacc,
            "drowsyCount": drowsy
        })
    
    return result


@router.get("/safe-driving/best-drivers", response_model=List[dict])
async def get_best_drivers(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    limit: int = Query(5, description="상위 N명"),
    db: Session = Depends(get_db)
):
    """베스트 드라이버 조회 (급가속, 급감속, 운전자태도 기준)"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 차량별 안전운전 점수 계산
    driver_scores = db.query(
        UserVehicle.car_id,
        func.count(func.distinct(DrivingSession.session_id)).label('session_count'),
        func.count(DrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((DrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((DrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((DrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy'),
        func.sum(case((DrivingSessionInfo.app_travel == 1, 1), else_=0)).label('total_travel'),
        UserVehicle.user_location
    ).join(
        DrivingSession, UserVehicle.car_id == DrivingSession.car_id
    ).join(
        DrivingSessionInfo, DrivingSession.session_id == DrivingSessionInfo.session_id
    ).outerjoin(
        DrowsyDrive, DrivingSession.session_id == DrowsyDrive.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end
    ).group_by(UserVehicle.car_id, UserVehicle.user_location).all()
    
    result = []
    for row in driver_scores:
        session_count = row.session_count or 0
        total_data_points = row.total_data_points or 1
        rapid_acc = int(row.rapid_acc or 0)
        rapid_deacc = int(row.rapid_deacc or 0)
        drowsy = int(row.drowsy or 0)
        total_travel = int(row.total_travel or 0)
        
        # 안전운전 점수 계산 (실제 데이터 포인트 기반)
        total_incidents = rapid_acc + rapid_deacc + drowsy
        if total_data_points > 0:
            base_score = max(0, min(100, 100 - (total_incidents / total_data_points * 100)))
        else:
            base_score = 100
        
        # 세션 수와 주행 거리 보너스 (안전운전을 많이 한 경우)
        session_bonus = min(3, session_count / 50)  # 최대 3점 (50회 이상)
        travel_bonus = min(2, total_travel / 500)  # 최대 2점 (500회 이상)
        
        final_score = min(100, base_score + session_bonus + travel_bonus)
        
        # 구 추출
        location = row.user_location or "부산시"
        district = "기타"
        if location and "구" in location:
            parts = location.split()
            for part in parts:
                if "구" in part:
                    idx = part.find("구")
                    if idx >= 0:
                        district = part[:idx+1] if idx > 0 else part
                    break
        
        result.append({
            "carId": row.car_id,
            "safetyScore": round(final_score, 1),
            "sessionCount": session_count,
            "rapidAccelCount": rapid_acc,
            "rapidDecelCount": rapid_deacc,
            "drowsyCount": drowsy,
            "totalTravel": total_travel,
            "district": district
        })
    
    # 점수 기준으로 정렬하고 상위 N명 반환
    result.sort(key=lambda x: x['safetyScore'], reverse=True)
    
    # 순위 추가
    for i, item in enumerate(result[:limit], 1):
        item['rank'] = i
    
    return result[:limit]


@router.get("/safe-driving/hourly", response_model=List[dict])
async def get_hourly_safe_driving(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_db)
):
    """시간대별 안전운전률 조회"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 시간대 그룹화
    hour_group = case(
        (and_(DrivingSessionInfo.Hour >= 0, DrivingSessionInfo.Hour < 6), '00-06시'),
        (and_(DrivingSessionInfo.Hour >= 6, DrivingSessionInfo.Hour < 9), '06-09시'),
        (and_(DrivingSessionInfo.Hour >= 9, DrivingSessionInfo.Hour < 12), '09-12시'),
        (and_(DrivingSessionInfo.Hour >= 12, DrivingSessionInfo.Hour < 15), '12-15시'),
        (and_(DrivingSessionInfo.Hour >= 15, DrivingSessionInfo.Hour < 18), '15-18시'),
        (and_(DrivingSessionInfo.Hour >= 18, DrivingSessionInfo.Hour < 21), '18-21시'),
        (DrivingSessionInfo.Hour >= 21, '21-24시'),
        else_='기타'
    )
    
    hourly_stats = db.query(
        hour_group.label('hour_range'),
        func.count(func.distinct(DrivingSession.session_id)).label('driving_count'),
        func.count(DrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((DrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((DrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((DrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy')
    ).join(
        DrivingSession, DrivingSessionInfo.session_id == DrivingSession.session_id
    ).outerjoin(
        DrowsyDrive, DrivingSession.session_id == DrowsyDrive.session_id
    ).filter(
        DrivingSession.start_time >= month_start,
        DrivingSession.start_time < month_end,
        DrivingSessionInfo.Hour.isnot(None)
    ).group_by('hour_range').all()
    
    result = []
    for row in hourly_stats:
        hour_range = row.hour_range or "기타"
        driving_count = row.driving_count or 0
        total_data_points = row.total_data_points or 1
        rapid_acc = int(row.rapid_acc or 0)
        rapid_deacc = int(row.rapid_deacc or 0)
        drowsy = int(row.drowsy or 0)
        
        total_incidents = rapid_acc + rapid_deacc + drowsy
        if total_data_points > 0:
            safety_rate = max(0, min(100, 100 - (total_incidents / total_data_points * 100)))
        else:
            safety_rate = 100
        
        result.append({
            "hourRange": hour_range,
            "safetyRate": round(safety_rate, 1),
            "drivingCount": driving_count,
            "rapidAccelCount": rapid_acc,
            "rapidDecelCount": rapid_deacc,
            "drowsyCount": drowsy
        })
    
    # 시간대 순서대로 정렬
    hour_order = {
        '00-06시': 0, '06-09시': 1, '09-12시': 2, '12-15시': 3,
        '15-18시': 4, '18-21시': 5, '21-24시': 6, '기타': 7
    }
    result.sort(key=lambda x: hour_order.get(x['hourRange'], 99))
    
    return result


@router.get("/safe-driving/top-drowsy-session", response_model=dict)
async def get_top_drowsy_session(
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_db)
):
    """gaze_closure 총 횟수가 가장 많은 session_id 조회"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = now.year
    
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # session_id별 gaze_closure 총합 계산
    top_session = db.query(
        DrowsyDrive.session_id,
        func.sum(DrowsyDrive.gaze_closure).label('total_gaze_closure'),
        func.count(DrowsyDrive.drowsy_id).label('detection_count')
    ).filter(
        DrowsyDrive.detected_at >= month_start,
        DrowsyDrive.detected_at < month_end,
        DrowsyDrive.gaze_closure.isnot(None)
    ).group_by(DrowsyDrive.session_id).order_by(
        func.sum(DrowsyDrive.gaze_closure).desc()
    ).first()
    
    if top_session:
        return {
            "sessionId": top_session.session_id,
            "totalGazeClosure": int(top_session.total_gaze_closure or 0),
            "detectionCount": top_session.detection_count or 0,
            "month": target_month,
            "year": target_year
        }
    else:
        return {
            "sessionId": None,
            "totalGazeClosure": 0,
            "detectionCount": 0,
            "month": target_month,
            "year": target_year
        }


@router.get("/safe-driving/best-drivers/monthly", response_model=List[dict])
async def get_best_drivers_monthly(
    year: int = Query(..., description="연도 (예: 2024)"),
    month: int = Query(..., description="월 (1-12)"),
    db: Session = Depends(get_db)
):
    """
    월별 베스트 드라이버 Top 10 조회 (createdDate 기준)
    
    점수 계산 기준:
    - 급가속 (app_rapid_acc) - 낮을수록 좋음
    - 급감속 (app_rapid_deacc) - 낮을수록 좋음
    - 눈 감음 횟수 (gaze_closure) - 낮을수록 좋음
    
    점수 = 1000 - (급가속 합계 + 급감속 합계 + 눈감음 합계) * 가중치
    """
    # 월별 베스트 드라이버를 계산하는 SQL 쿼리 (createdDate 기준)
    # MySQL에서는 ORDER BY에서 별칭을 직접 사용할 수 없으므로 집계 함수를 다시 사용
    query = text("""
        SELECT 
            ds.car_id,
            uv.user_car_brand,
            uv.user_car_model,
            uv.age,
            uv.user_sex,
            uv.user_location,
            COALESCE(SUM(COALESCE(dsi.app_rapid_acc, 0)), 0) as total_rapid_acc,
            COALESCE(SUM(COALESCE(dsi.app_rapid_deacc, 0)), 0) as total_rapid_deacc,
            COALESCE(SUM(COALESCE(dd.gaze_closure, 0)), 0) as total_gaze_closure,
            COUNT(DISTINCT ds.session_id) as session_count
        FROM driving_session ds
        LEFT JOIN uservehicle uv ON ds.car_id = uv.car_id
        LEFT JOIN driving_session_info dsi ON ds.session_id = dsi.session_id
        LEFT JOIN drowsy_drive dd ON ds.session_id = dd.session_id
        WHERE YEAR(dsi.createdDate) = :year
          AND MONTH(dsi.createdDate) = :month
          AND dsi.createdDate IS NOT NULL
        GROUP BY ds.car_id, uv.user_car_brand, uv.user_car_model, uv.age, uv.user_sex, uv.user_location
        HAVING COUNT(DISTINCT ds.session_id) > 0
        ORDER BY (
            (COALESCE(SUM(COALESCE(dsi.app_rapid_acc, 0)), 0) + 
             COALESCE(SUM(COALESCE(dsi.app_rapid_deacc, 0)), 0) + 
             COALESCE(SUM(COALESCE(dd.gaze_closure, 0)), 0)) / 
            NULLIF(COUNT(DISTINCT ds.session_id), 0)
        ) ASC
        LIMIT 10
    """)
    
    result = db.execute(query, {"year": year, "month": month})
    rows = result.fetchall()
    
    best_drivers = []
    for idx, row in enumerate(rows, 1):
        total_rapid_acc = row[6] or 0
        total_rapid_deacc = row[7] or 0
        total_gaze_closure = row[8] or 0
        session_count = row[9] or 1  # 0으로 나누기 방지
        
        # 총 사고 횟수
        total_incidents = total_rapid_acc + total_rapid_deacc + total_gaze_closure
        
        # 발생률 계산 (세션당 평균 사고 횟수)
        # 세션 수가 많을수록 더 공정한 평가를 위해 발생률 사용
        if session_count > 0:
            incident_rate = total_incidents / session_count
        else:
            incident_rate = 0
        
        # 점수 계산: 발생률 기반 (낮을수록 좋음)
        # 발생률 0.0 = 1000점, 발생률 1.0 = 0점
        # 발생률이 0.1 (세션당 0.1회) = 900점
        driver_score = max(0, 1000 - (incident_rate * 1000))
        
        best_drivers.append({
            "rank": idx,
            "carId": row[0],
            "carBrand": row[1],
            "carModel": row[2],
            "driverAge": row[3],
            "driverSex": row[4],
            "driverLocation": row[5],
            "totalRapidAcc": int(total_rapid_acc),
            "totalRapidDeacc": int(total_rapid_deacc),
            "totalGazeClosure": int(total_gaze_closure),
            "totalScore": int(total_incidents),
            "driverScore": round(driver_score, 2),
            "sessionCount": session_count,
            "incidentRate": round(incident_rate, 4)  # 발생률 추가
        })
    
    return best_drivers
