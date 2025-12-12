"""
경찰청 관리자 API
실종자 탐지 알림 및 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.database import get_busan_car_db, get_web_db
from app.api.deps import require_police_admin
from app.models.user import User
from app.models.missing_person_detection import MissingPersonDetection
from app.models.missing_person_info import MissingPersonInfo
from app.models.missing_person_detection_modification import MissingPersonDetectionModification
from app.models.missing_person_detection_modification import MissingPersonDetectionModification

router = APIRouter()


class UpdateDetectionRequest(BaseModel):
    detection_success: bool


@router.get("/missing-person/detections", response_model=dict)
async def get_missing_person_detections(
    missing_id: Optional[str] = Query(None, description="실종자 ID로 필터링"),
    detection_success: Optional[str] = Query(None, description="탐지 성공 여부로 필터링 (true/false/null)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    limit: int = Query(100, ge=1, le=1000, description="페이지당 항목 수 (최대 1000)"),
    current_user: User = Depends(require_police_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    실종자 탐지 알림 조회 (위치, 시간)
    경찰청 관리자 전용
    페이지네이션 지원
    """
    query = busan_car_db.query(MissingPersonDetection, MissingPersonInfo).outerjoin(
        MissingPersonInfo, MissingPersonDetection.missing_id == MissingPersonInfo.missing_id
    )
    
    # 필터링
    if missing_id:
        query = query.filter(MissingPersonDetection.missing_id == missing_id)
    
    if detection_success is not None:
        # detection_success가 'true'면 1, 'false'면 0, 'null'이면 NULL 필터링
        if detection_success.lower() == 'true':
            query = query.filter(MissingPersonDetection.detection_success == 1)
        elif detection_success.lower() == 'false':
            query = query.filter(MissingPersonDetection.detection_success == 0)
        elif detection_success.lower() == 'null':
            # NULL 필터링 (미확인)
            query = query.filter(MissingPersonDetection.detection_success.is_(None))
    
    if start_date:
        query = query.filter(MissingPersonDetection.detected_time >= start_date)
    
    if end_date:
        # end_date는 해당 월의 마지막 날 23:59:59이므로, 다음 날 00:00:00 미만으로 필터링
        # 통계와 동일한 로직 적용 (다음 달 1일 00:00:00 미만)
        from datetime import timedelta
        end_date_exclusive = end_date + timedelta(seconds=1)  # 1초 추가하여 다음 날 00:00:00으로 변환
        query = query.filter(MissingPersonDetection.detected_time < end_date_exclusive)
    
    # 총 개수 계산 (필터링 후)
    total_count = query.count()
    
    # 페이지네이션 적용
    offset = (page - 1) * limit
    results = query.order_by(MissingPersonDetection.detected_time.desc()).offset(offset).limit(limit).all()
    
    # 총 페이지 수 계산
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    
    # 해결완료 여부 조회 (web DB)
    detection_ids = [detection.detection_id for detection, _ in results]
    resolved_detections = {}
    if detection_ids:
        resolved_records = web_db.query(MissingPersonDetectionModification).filter(
            MissingPersonDetectionModification.detection_id.in_(detection_ids),
            MissingPersonDetectionModification.is_resolved == True
        ).all()
        resolved_detections = {r.detection_id: True for r in resolved_records}
    
    items = []
    for detection, info in results:
        is_resolved = resolved_detections.get(detection.detection_id, False)
        items.append({
            "detectionId": detection.detection_id,
            "missingId": detection.missing_id or "알 수 없음",
            "missingName": info.missing_name if info else "알 수 없음",
            "missingAge": info.missing_age if info else None,
            "imageId": detection.image_id,
            "detectionSuccess": bool(detection.detection_success) if detection.detection_success is not None else None,
            "detectedLat": detection.detected_lat,
            "detectedLon": detection.detected_lon,
            "detectedTime": detection.detected_time.isoformat() if detection.detected_time else None,
            "location": f"위도: {detection.detected_lat}, 경도: {detection.detected_lon}" if detection.detected_lat and detection.detected_lon else "위치 정보 없음",
            "isResolved": is_resolved
        })
    
    return {
        "items": items,
        "total": total_count,
        "page": page,
        "limit": limit,
        "totalPages": total_pages
    }


@router.get("/missing-person/detections/recent", response_model=List[dict])
async def get_recent_missing_person_detections(
    since: Optional[datetime] = Query(None, description="이 시간 이후의 탐지 기록 조회"),
    current_user: User = Depends(require_police_admin),
    db: Session = Depends(get_busan_car_db)
):
    """
    최신 실종자 탐지 기록 조회 (알림용)
    경찰청 관리자 전용
    특정 시간 이후의 새로운 탐지 기록만 반환
    """
    query = db.query(MissingPersonDetection, MissingPersonInfo).outerjoin(
        MissingPersonInfo, MissingPersonDetection.missing_id == MissingPersonInfo.missing_id
    )
    
    # 특정 시간 이후의 탐지 기록만 조회
    if since:
        query = query.filter(MissingPersonDetection.detected_time > since)
    
    # 최신순 정렬, 최대 50개만 반환 (알림용이므로)
    results = query.order_by(MissingPersonDetection.detected_time.desc()).limit(50).all()
    
    items = []
    for detection, info in results:
        items.append({
            "detectionId": detection.detection_id,
            "missingId": detection.missing_id or "알 수 없음",
            "missingName": info.missing_name if info else "알 수 없음",
            "missingAge": info.missing_age if info else None,
            "detectionSuccess": bool(detection.detection_success) if detection.detection_success is not None else None,
            "detectedLat": detection.detected_lat,
            "detectedLon": detection.detected_lon,
            "detectedTime": detection.detected_time.isoformat() if detection.detected_time else None,
            "location": f"위도: {detection.detected_lat}, 경도: {detection.detected_lon}" if detection.detected_lat and detection.detected_lon else "위치 정보 없음"
        })
    
    return items


@router.put("/missing-person/detections/{detection_id}", response_model=dict)
async def update_detection_result(
    detection_id: str,
    request: UpdateDetectionRequest,
    current_user: User = Depends(require_police_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    탐지 결과 수정 기능
    경찰청 관리자 전용
    web DB에 수정 기록 저장
    """
    # 탐지 기록 조회 (busan_car DB)
    detection = busan_car_db.query(MissingPersonDetection).filter(
        MissingPersonDetection.detection_id == detection_id
    ).first()
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탐지 기록을 찾을 수 없습니다"
        )
    
    # 이전 탐지 결과 저장 (수정 기록용)
    previous_result = bool(detection.detection_success) if detection.detection_success is not None else None
    
    # 탐지 결과 업데이트 (busan_car DB)
    detection.detection_success = 1 if request.detection_success else 0
    busan_car_db.commit()
    busan_car_db.refresh(detection)
    
    # 기존 수정 기록 확인 (같은 missing_id와 detection_id)
    missing_id = detection.missing_id or "알 수 없음"
    existing_modification = web_db.query(MissingPersonDetectionModification).filter(
        MissingPersonDetectionModification.detection_id == detection_id,
        MissingPersonDetectionModification.missing_id == missing_id
    ).first()
    
    if existing_modification:
        # 기존 행 업데이트
        # 탐지 결과 수정 시에는 is_resolved와 resolved_at은 변경하지 않음
        existing_modification.previous_result = previous_result
        existing_modification.new_result = request.detection_success
        existing_modification.modified_by_user_id = current_user.id
        # is_resolved와 resolved_at은 해결완료 처리할 때만 변경됨
        # updated_at은 onupdate로 자동 업데이트됨
        web_db.commit()
        web_db.refresh(existing_modification)
    else:
        # 새 행 생성
        modification = MissingPersonDetectionModification(
            detection_id=detection_id,
            missing_id=missing_id,
            previous_result=previous_result,
            new_result=request.detection_success,
            modified_by_user_id=current_user.id
        )
        web_db.add(modification)
        web_db.commit()
        web_db.refresh(modification)
    
    return {
        "detectionId": detection.detection_id,
        "missingId": detection.missing_id,
        "detectionSuccess": bool(detection.detection_success),
        "message": "탐지 결과가 수정되었습니다"
    }


@router.put("/missing-person/detections/{detection_id}/resolve", response_model=dict)
async def resolve_missing_person(
    detection_id: str,
    current_user: User = Depends(require_police_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    실종자 해결완료 처리
    경찰청 관리자 전용
    web DB에 해결완료 기록 저장
    """
    # 탐지 기록 조회 (busan_car DB)
    detection = busan_car_db.query(MissingPersonDetection).filter(
        MissingPersonDetection.detection_id == detection_id
    ).first()
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탐지 기록을 찾을 수 없습니다"
        )
    
    missing_id = detection.missing_id or "알 수 없음"
    
    # 기존 수정 기록 확인 (같은 missing_id와 detection_id)
    existing_modification = web_db.query(MissingPersonDetectionModification).filter(
        MissingPersonDetectionModification.detection_id == detection_id,
        MissingPersonDetectionModification.missing_id == missing_id
    ).first()
    
    # 이미 해결완료 처리되었는지 확인
    if existing_modification and existing_modification.is_resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 해결완료 처리된 탐지입니다"
        )
    
    # 해결완료 기록 저장/업데이트 (web DB)
    # 해결완료는 탐지 결과와 별개이므로 new_result는 변경하지 않음
    from datetime import datetime
    if existing_modification:
        # 기존 행 업데이트: is_resolved와 resolved_at만 설정
        # new_result와 previous_result는 그대로 유지 (탐지 결과 수정과 별개)
        existing_modification.is_resolved = True
        existing_modification.resolved_at = datetime.now()
        # updated_at은 onupdate로 자동 업데이트됨
        web_db.commit()
        web_db.refresh(existing_modification)
        resolution = existing_modification
    else:
        # 새 행 생성: 현재 탐지 결과를 그대로 유지
        current_result = bool(detection.detection_success) if detection.detection_success is not None else None
        resolution = MissingPersonDetectionModification(
            detection_id=detection_id,
            missing_id=missing_id,
            previous_result=None,  # 해결완료만 처리하는 경우 previous_result는 없음
            new_result=current_result,  # 현재 탐지 결과 유지
            modified_by_user_id=current_user.id,
            is_resolved=True,
            resolved_at=datetime.now()
        )
        web_db.add(resolution)
        web_db.commit()
        web_db.refresh(resolution)
    
    return {
        "detectionId": detection.detection_id,
        "missingId": detection.missing_id,
        "isResolved": True,
        "resolvedAt": resolution.resolved_at.isoformat() if resolution.resolved_at else None,
        "message": "해결완료 처리되었습니다"
    }


@router.get("/missing-person/stats", response_model=dict)
async def get_missing_person_stats(
    year: Optional[int] = Query(None, description="년도 (예: 2024)"),
    month: Optional[int] = Query(None, description="월 (1-12)"),
    current_user: User = Depends(require_police_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    실종자 통계 조회
    - 오늘 탐지 건수
    - 월간 탐지 건수 (선택한 년도/월 기준, 없으면 이번 달)
    """
    # 오늘 날짜
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 오늘 탐지 건수 (detection_success = true인 것만 카운트)
    today_count = busan_car_db.query(func.count(MissingPersonDetection.detection_id)).filter(
        MissingPersonDetection.detected_time >= today,
        MissingPersonDetection.detection_success == 1  # 탐지 성공한 것만 카운트
    ).scalar() or 0
    
    # 월간 탐지 건수 계산
    if year and month:
        # 선택한 년도/월의 첫 날과 마지막 날
        first_day_of_month = datetime(year, month, 1, 0, 0, 0)
        if month == 12:
            last_day_of_month = datetime(year + 1, 1, 1, 0, 0, 0)
        else:
            last_day_of_month = datetime(year, month + 1, 1, 0, 0, 0)
    else:
        # 기본값: 이번 달
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if datetime.now().month == 12:
            last_day_of_month = datetime(datetime.now().year + 1, 1, 1, 0, 0, 0)
        else:
            last_day_of_month = datetime(datetime.now().year, datetime.now().month + 1, 1, 0, 0, 0)
    
    # 월간 탐지 건수 (detected_time 기준이지만, detection_success = true인 것만 카운트)
    # 미탐지로 수정한 것은 잘못 탐지된 것이므로 통계에서 제외
    monthly_count = busan_car_db.query(func.count(MissingPersonDetection.detection_id)).filter(
        MissingPersonDetection.detected_time.isnot(None),  # NULL 제외
        MissingPersonDetection.detected_time >= first_day_of_month,
        MissingPersonDetection.detected_time < last_day_of_month,
        MissingPersonDetection.detection_success == 1  # 탐지 성공한 것만 카운트
    ).scalar() or 0
    
    # 해결완료 건수 (web DB에서 is_resolved = True인 것)
    resolved_count = web_db.query(func.count(MissingPersonDetectionModification.id)).filter(
        MissingPersonDetectionModification.is_resolved == True,
        MissingPersonDetectionModification.resolved_at >= first_day_of_month,
        MissingPersonDetectionModification.resolved_at < last_day_of_month
    ).scalar() or 0
    
    return {
        "missingToday": today_count,
        "missingMonthly": monthly_count,
        "resolvedCount": resolved_count
    }

