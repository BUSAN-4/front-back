from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, extract, text
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.database import get_busan_car_db, get_web_db
from app.api.deps import require_busan_admin
from app.models.user import User
from app.models.missing_person_detection import MissingPersonDetection
from app.models.missing_person_info import MissingPersonInfo
from app.models.arrears_detection import ArrearsDetection
from app.models.arrears_info import ArrearsInfo
from app.models.missing_person_detection_modification import MissingPersonDetectionModification
from app.models.arrears_detection_modification import ArrearsDetectionModification
from app.models.busan_car_models import (
    BusanCarDrivingSession,
    BusanCarDrivingSessionInfo,
    BusanCarDrowsyDrive,
    BusanCarUserVehicle
)

router = APIRouter()


@router.get("/missing-person", response_model=List[dict])
async def get_missing_person_detections(
    missing_id: Optional[str] = Query(None, description="실종자 ID로 필터링"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_busan_car_db)
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
        "detectedTime": d.detected_time.isoformat() if d.detected_time else None
    } for d in detections]


@router.get("/missing-person/stats", response_model=dict)
async def get_missing_person_stats(
    current_user: User = Depends(require_busan_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    실종자 통계 조회 (부산시청 관리자용)
    - 이번달 실종 신고 수 (missing_person_info 테이블의 registered_at 기준)
    - 이번달 실종자 탐지 수 (missing_person_detection에서 detection_success = 1)
    - 해결률 (해결완료 수 / 신고 수 * 100)
    """
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1, 0, 0, 0)
    if now.month == 12:
        month_end = datetime(now.year + 1, 1, 1, 0, 0, 0)
    else:
        month_end = datetime(now.year, now.month + 1, 1, 0, 0, 0)
    
    # 이번달 실종 신고 수 (missing_person_info의 registered_at 기준)
    monthly_reports = busan_car_db.query(func.count(MissingPersonInfo.missing_id)).filter(
        MissingPersonInfo.registered_at >= month_start,
        MissingPersonInfo.registered_at < month_end
    ).scalar() or 0
    
    # 이번달 실종자 탐지 수 (missing_person_detection에서 detection_success = 1인 것만)
    monthly_found = busan_car_db.query(func.count(MissingPersonDetection.detection_id)).filter(
        MissingPersonDetection.detected_time >= month_start,
        MissingPersonDetection.detected_time < month_end,
        MissingPersonDetection.detection_success == 1
    ).scalar() or 0
    
    # 해결완료 수 (web DB에서 is_resolved = True인 것)
    resolved_count = web_db.query(func.count(MissingPersonDetectionModification.id)).filter(
        MissingPersonDetectionModification.is_resolved == True,
        MissingPersonDetectionModification.resolved_at >= month_start,
        MissingPersonDetectionModification.resolved_at < month_end
    ).scalar() or 0
    
    # 해결률 계산 (해결완료 수 / 신고 수 * 100)
    resolution_rate = 0
    if monthly_reports > 0:
        resolution_rate = round((resolved_count / monthly_reports) * 100, 1)
    
    # 월별 추이 (최근 7개월)
    monthly_trend = []
    month_list = []
    for i in range(6, -1, -1):  # 6개월 전부터 현재까지
        target_year = now.year
        target_month = now.month - i
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1
        month_list.append((target_year, target_month))
    
    for year, month in month_list:
        month_start = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            month_end = datetime(year + 1, 1, 1, 0, 0, 0)
        else:
            month_end = datetime(year, month + 1, 1, 0, 0, 0)
        
        # 해당 월의 실종 신고 수
        month_reports = busan_car_db.query(func.count(MissingPersonInfo.missing_id)).filter(
            MissingPersonInfo.registered_at >= month_start,
            MissingPersonInfo.registered_at < month_end
        ).scalar() or 0
        
        # 해당 월의 실종자 탐지 수 (detection_success = 1인 것만)
        month_found = busan_car_db.query(func.count(MissingPersonDetection.detection_id)).filter(
            MissingPersonDetection.detected_time >= month_start,
            MissingPersonDetection.detected_time < month_end,
            MissingPersonDetection.detection_success == 1
        ).scalar() or 0
        
        # 해당 월의 해결완료 수
        month_resolved = web_db.query(func.count(MissingPersonDetectionModification.id)).filter(
            MissingPersonDetectionModification.is_resolved == True,
            MissingPersonDetectionModification.resolved_at >= month_start,
            MissingPersonDetectionModification.resolved_at < month_end
        ).scalar() or 0
        
        # 해결률 계산
        month_resolution_rate = 0
        if month_reports > 0:
            month_resolution_rate = round((month_resolved / month_reports) * 100, 1)
        
        monthly_trend.append({
            "month": f"{year}-{month:02d}",
            "reports": month_reports,
            "found": month_found,
            "resolved": month_resolved,
            "resolutionRate": month_resolution_rate
        })
    
    return {
        "monthlyReports": monthly_reports,
        "monthlyFound": monthly_found,
        "resolutionRate": resolution_rate,
        "resolvedCount": resolved_count,
        "monthlyTrend": monthly_trend
    }


@router.get("/arrears", response_model=List[dict])
async def get_arrears_detections(
    car_plate_number: Optional[str] = Query(None, description="차량 번호로 필터링"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_busan_car_db)
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


@router.get("/arrears/detections/today", response_model=List[dict])
async def get_today_arrears_detections(
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_busan_car_db)
):
    """
    오늘 탐지된 체납 차량 목록 조회 (부산시청 관리자용)
    arrears_detection과 arrears_info를 조인하여 체납 금액, 기간 등 정보 포함
    """
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
    
    # 오늘 탐지된 체납 차량 조회 (arrears_detection과 arrears_info 조인)
    detections = db.query(
        ArrearsDetection,
        ArrearsInfo
    ).outerjoin(
        ArrearsInfo, ArrearsDetection.car_plate_number == ArrearsInfo.car_plate_number
    ).filter(
        ArrearsDetection.detected_time >= today_start,
        ArrearsDetection.detected_time <= today_end
    ).order_by(ArrearsDetection.detected_time.desc()).all()
    
    result = []
    for detection, info in detections:
        # 위치 정보 생성
        location = "위치 정보 없음"
        if detection.detected_lat and detection.detected_lon:
            location = f"위도: {detection.detected_lat:.6f}, 경도: {detection.detected_lon:.6f}"
        
        result.append({
            "detectionId": detection.detection_id,
            "carPlateNumber": detection.car_plate_number or "알 수 없음",
            "detectedLat": detection.detected_lat,
            "detectedLon": detection.detected_lon,
            "detectedTime": detection.detected_time.isoformat() if detection.detected_time else None,
            "location": location,
            "detectionSuccess": bool(detection.detection_success) if detection.detection_success is not None else None,
            "totalArrearsAmount": info.total_arrears_amount if info else None,
            "arrearsPeriod": info.arrears_period if info else None,
            "noticeSent": bool(info.notice_sent) if info and info.notice_sent is not None else False
        })
    
    return result


@router.get("/arrears/stats", response_model=dict)
async def get_arrears_stats(
    current_user: User = Depends(require_busan_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    체납자 통계 조회 (부산시청 관리자용)
    - 오늘 탐지된 체납 차량 수
    - 월별 신규 체납자 추이 (최근 7개월)
    - 총 체납 금액 (arrears_info 테이블의 total_arrears_amount 합계)
    - 해결률 (해결완료 수 / 신규 체납자 수 * 100)
    """
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
    today_end = datetime(now.year, now.month, now.day, 23, 59, 59)
    
    # 오늘 탐지된 체납 차량 수
    today_detected = busan_car_db.query(func.count(ArrearsDetection.detection_id)).filter(
        ArrearsDetection.detected_time >= today_start,
        ArrearsDetection.detected_time <= today_end
    ).scalar() or 0
    
    # 총 체납 금액 (arrears_info 테이블의 total_arrears_amount 합계)
    total_amount = busan_car_db.query(func.sum(ArrearsInfo.total_arrears_amount)).scalar() or 0
    
    # 월별 신규 체납자 추이 (최근 7개월)
    # arrears_info 테이블의 arrears_period 컬럼에서 시작 월 추출하여 집계
    # SQL: SELECT SUBSTRING_INDEX(arrears_period, '~', 1) AS start_month, COUNT(*) FROM arrears_info GROUP BY start_month
    monthly_trend = []
    
    # 최근 7개월 목록 생성
    month_list = []
    for i in range(6, -1, -1):  # 6개월 전부터 현재까지
        target_year = now.year
        target_month = now.month - i
        
        # 월이 음수가 되면 이전 년도로 조정
        while target_month <= 0:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1
        
        month_list.append(f"{target_year}.{target_month:02d}")
    
    # arrears_info 테이블에서 월별 신규 체납자 집계 (arrears_period의 시작 월 기준)
    query = text("""
        SELECT 
            SUBSTRING_INDEX(arrears_period, '~', 1) AS start_month,
            COUNT(*) AS new_arrears_count
        FROM arrears_info
        WHERE arrears_period IS NOT NULL
        GROUP BY start_month
        ORDER BY start_month DESC
    """)
    
    result = busan_car_db.execute(query)
    monthly_data = {row[0]: row[1] for row in result.fetchall()}
    
    # 최근 7개월에 대해 데이터 구성 (없는 월은 0으로)
    for month_str in month_list:
        monthly_trend.append({
            "month": month_str.replace('.', '-'),  # "2025.12" -> "2025-12" 형식으로 변환
            "count": monthly_data.get(month_str, 0)
        })
    
    # 이번달 해결완료 수 (web DB에서 is_resolved = True인 것)
    month_start = datetime(now.year, now.month, 1, 0, 0, 0)
    if now.month == 12:
        month_end = datetime(now.year + 1, 1, 1, 0, 0, 0)
    else:
        month_end = datetime(now.year, now.month + 1, 1, 0, 0, 0)
    
    resolved_count = web_db.query(func.count(ArrearsDetectionModification.id)).filter(
        ArrearsDetectionModification.is_resolved == True,
        ArrearsDetectionModification.resolved_at >= month_start,
        ArrearsDetectionModification.resolved_at < month_end
    ).scalar() or 0
    
    # 이번달 신규 체납자 수 (arrears_period가 이번달인 것)
    current_month_str = f"{now.year}.{now.month:02d}"
    monthly_new = busan_car_db.execute(text("""
        SELECT COUNT(*) 
        FROM arrears_info 
        WHERE SUBSTRING_INDEX(arrears_period, '~', 1) = :month_str
    """), {"month_str": current_month_str}).scalar() or 0
    
    # 해결률 계산 (해결완료 수 / 신규 체납자 수 * 100)
    resolution_rate = 0
    if monthly_new > 0:
        resolution_rate = round((resolved_count / monthly_new) * 100, 1)
    
    return {
        "todayDetected": today_detected,
        "totalAmount": int(total_amount),
        "monthlyTrend": monthly_trend,
        "resolvedCount": resolved_count,
        "resolutionRate": resolution_rate
    }


@router.get("/drowsy-drive", response_model=List[dict])
async def get_drowsy_drive_detections(
    session_id: Optional[str] = Query(None, description="세션 ID로 필터링"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    current_user: User = Depends(require_busan_admin),
    db: Session = Depends(get_busan_car_db)
):
    """운전자 운전태도(졸음운전) 실시간 탐지 조회 (drowsy_drive 테이블)"""
    query = db.query(BusanCarDrowsyDrive)
    
    if session_id:
        query = query.filter(BusanCarDrowsyDrive.session_id == session_id)
    
    if start_date:
        query = query.filter(BusanCarDrowsyDrive.detected_at >= start_date)
    
    if end_date:
        query = query.filter(BusanCarDrowsyDrive.detected_at <= end_date)
    
    detections = query.order_by(BusanCarDrowsyDrive.detected_at.desc()).all()
    
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
    db: Session = Depends(get_busan_car_db)
):
    """실제 DB에 있는 car_id 샘플 조회 (디버깅용)"""
    car_ids = db.query(BusanCarUserVehicle.car_id).limit(limit).all()
    return [row.car_id for row in car_ids if row.car_id]


@router.get("/safe-driving/stats", response_model=dict)
async def get_safe_driving_stats(
    year: Optional[int] = Query(None, description="연도 (예: 2024), None이면 현재 연도"),
    month: Optional[int] = Query(None, description="월 (1-12), None이면 현재 월"),
    db: Session = Depends(get_busan_car_db)
):
    """안전운전 주요 지표 조회 (주행 차량 수, 전체 안전운전율)"""
    now = datetime.now()
    target_month = month if month else now.month
    target_year = year if year else now.year
    
    # 현재 주행 중인 차량 수 (end_time이 NULL이거나 미래인 세션)
    active_sessions = db.query(BusanCarDrivingSession).filter(
        or_(
            BusanCarDrivingSession.end_time.is_(None),
            BusanCarDrivingSession.end_time > now
        )
    ).count()
    
    # 해당 월의 전체 세션 수
    month_sessions = db.query(BusanCarDrivingSession).filter(
        extract('year', BusanCarDrivingSession.start_time) == target_year,
        extract('month', BusanCarDrivingSession.start_time) == target_month
    ).count()
    
    # 해당 월의 안전운전 데이터 집계
    month_start = datetime(target_year, target_month, 1)
    if target_month == 12:
        month_end = datetime(target_year + 1, 1, 1)
    else:
        month_end = datetime(target_year, target_month + 1, 1)
    
    # 급가속, 급감속, 졸음운전 집계 (dt 기준)
    rapid_acc_count = db.query(func.count(BusanCarDrivingSessionInfo.info_id)).join(
        BusanCarDrivingSession, BusanCarDrivingSessionInfo.session_id == BusanCarDrivingSession.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None),
        BusanCarDrivingSessionInfo.app_rapid_acc > 0
    ).scalar() or 0
    
    rapid_deacc_count = db.query(func.count(BusanCarDrivingSessionInfo.info_id)).join(
        BusanCarDrivingSession, BusanCarDrivingSessionInfo.session_id == BusanCarDrivingSession.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None),
        BusanCarDrivingSessionInfo.app_rapid_deacc > 0
    ).scalar() or 0
    
    drowsy_count = db.query(func.count(BusanCarDrowsyDrive.drowsy_id)).filter(
        BusanCarDrowsyDrive.detected_at >= month_start,
        BusanCarDrowsyDrive.detected_at < month_end,
        BusanCarDrowsyDrive.abnormal_flag > 0
    ).scalar() or 0
    
    # 전체 데이터 포인트 수 (실제 driving_session_info 레코드 수, dt 기준)
    total_data_points = db.query(func.count(BusanCarDrivingSessionInfo.info_id)).join(
        BusanCarDrivingSession, BusanCarDrivingSessionInfo.session_id == BusanCarDrivingSession.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None)
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
    db: Session = Depends(get_busan_car_db)
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
    
    # 먼저 모든 데이터를 가져와서 Python에서 처리 (dt 기준)
    district_data = db.query(
        BusanCarUserVehicle.user_location,
        BusanCarDrivingSessionInfo.app_rapid_acc,
        BusanCarDrivingSessionInfo.app_rapid_deacc,
        BusanCarDrowsyDrive.abnormal_flag,
        BusanCarDrivingSession.session_id
    ).join(
        BusanCarDrivingSession, BusanCarUserVehicle.car_id == BusanCarDrivingSession.car_id
    ).join(
        BusanCarDrivingSessionInfo, BusanCarDrivingSession.session_id == BusanCarDrivingSessionInfo.session_id
    ).outerjoin(
        BusanCarDrowsyDrive, BusanCarDrivingSession.session_id == BusanCarDrowsyDrive.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None),
        BusanCarUserVehicle.user_location.isnot(None),
        BusanCarUserVehicle.user_location.like('%구%')
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
    db: Session = Depends(get_busan_car_db)
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
        (and_(BusanCarUserVehicle.age >= 20, BusanCarUserVehicle.age < 30), '20대'),
        (and_(BusanCarUserVehicle.age >= 30, BusanCarUserVehicle.age < 40), '30대'),
        (and_(BusanCarUserVehicle.age >= 40, BusanCarUserVehicle.age < 50), '40대'),
        (BusanCarUserVehicle.age >= 50, '50대 이상'),
        else_='기타'
    )
    
    demographics = db.query(
        BusanCarUserVehicle.user_sex.label('gender'),
        age_group.label('age_group'),
        func.count(func.distinct(BusanCarDrivingSession.session_id)).label('session_count'),
        func.count(BusanCarDrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((BusanCarDrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy')
    ).join(
        BusanCarDrivingSession, BusanCarUserVehicle.car_id == BusanCarDrivingSession.car_id
    ).join(
        BusanCarDrivingSessionInfo, BusanCarDrivingSession.session_id == BusanCarDrivingSessionInfo.session_id
    ).outerjoin(
        BusanCarDrowsyDrive, BusanCarDrivingSession.session_id == BusanCarDrowsyDrive.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None),
        BusanCarUserVehicle.user_sex.isnot(None),
        BusanCarUserVehicle.age.isnot(None)
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
    db: Session = Depends(get_busan_car_db)
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
    
    # 차량별 안전운전 점수 계산 (dt 기준)
    driver_scores = db.query(
        BusanCarUserVehicle.car_id,
        func.count(func.distinct(BusanCarDrivingSession.session_id)).label('session_count'),
        func.count(BusanCarDrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((BusanCarDrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy'),
        func.sum(case((BusanCarDrivingSessionInfo.app_travel == 1, 1), else_=0)).label('total_travel'),
        BusanCarUserVehicle.user_location
    ).join(
        BusanCarDrivingSession, BusanCarUserVehicle.car_id == BusanCarDrivingSession.car_id
    ).join(
        BusanCarDrivingSessionInfo, BusanCarDrivingSession.session_id == BusanCarDrivingSessionInfo.session_id
    ).outerjoin(
        BusanCarDrowsyDrive, BusanCarDrivingSession.session_id == BusanCarDrowsyDrive.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None)
    ).group_by(BusanCarUserVehicle.car_id, BusanCarUserVehicle.user_location).all()
    
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
    db: Session = Depends(get_busan_car_db)
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
        (and_(BusanCarDrivingSessionInfo.Hour >= 0, BusanCarDrivingSessionInfo.Hour < 6), '00-06시'),
        (and_(BusanCarDrivingSessionInfo.Hour >= 6, BusanCarDrivingSessionInfo.Hour < 9), '06-09시'),
        (and_(BusanCarDrivingSessionInfo.Hour >= 9, BusanCarDrivingSessionInfo.Hour < 12), '09-12시'),
        (and_(BusanCarDrivingSessionInfo.Hour >= 12, BusanCarDrivingSessionInfo.Hour < 15), '12-15시'),
        (and_(BusanCarDrivingSessionInfo.Hour >= 15, BusanCarDrivingSessionInfo.Hour < 18), '15-18시'),
        (and_(BusanCarDrivingSessionInfo.Hour >= 18, BusanCarDrivingSessionInfo.Hour < 21), '18-21시'),
        (BusanCarDrivingSessionInfo.Hour >= 21, '21-24시'),
        else_='기타'
    )
    
    hourly_stats = db.query(
        hour_group.label('hour_range'),
        func.count(func.distinct(BusanCarDrivingSession.session_id)).label('driving_count'),
        func.count(BusanCarDrivingSessionInfo.info_id).label('total_data_points'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_acc > 0, 1), else_=0)).label('rapid_acc'),
        func.sum(case((BusanCarDrivingSessionInfo.app_rapid_deacc > 0, 1), else_=0)).label('rapid_deacc'),
        func.sum(case((BusanCarDrowsyDrive.abnormal_flag > 0, 1), else_=0)).label('drowsy')
    ).join(
        BusanCarDrivingSession, BusanCarDrivingSessionInfo.session_id == BusanCarDrivingSession.session_id
    ).outerjoin(
        BusanCarDrowsyDrive, BusanCarDrivingSession.session_id == BusanCarDrowsyDrive.session_id
    ).filter(
        BusanCarDrivingSession.start_time >= month_start,
        BusanCarDrivingSession.start_time < month_end,
        BusanCarDrivingSessionInfo.dt.isnot(None),
        BusanCarDrivingSessionInfo.Hour.isnot(None)
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
    db: Session = Depends(get_busan_car_db)
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
        BusanCarDrowsyDrive.session_id,
        func.sum(BusanCarDrowsyDrive.gaze_closure).label('total_gaze_closure'),
        func.count(BusanCarDrowsyDrive.drowsy_id).label('detection_count')
    ).filter(
        BusanCarDrowsyDrive.detected_at >= month_start,
        BusanCarDrowsyDrive.detected_at < month_end,
        BusanCarDrowsyDrive.gaze_closure.isnot(None)
    ).group_by(BusanCarDrowsyDrive.session_id).order_by(
        func.sum(BusanCarDrowsyDrive.gaze_closure).desc()
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
    db: Session = Depends(get_busan_car_db)
):
    """
    월별 베스트 드라이버 Top 10 조회 (발생률 기반 점수 계산)
    
    점수 계산 방식:
    - 급가속, 급감속, 눈감음 총합을 세션 수로 나눈 발생률 계산
    - 발생률이 낮을수록 높은 점수 (1000점 만점)
    - 발생률 0.0 = 1000점, 발생률 1.0 = 0점
    """
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
