"""
국세청 관리자 API
체납자 차량 탐지 알림 및 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_busan_car_db, get_web_db
from app.api.deps import require_nts_admin
from app.models.user import User
from app.models.arrears_detection import ArrearsDetection
from app.models.arrears_info import ArrearsInfo
from app.models.arrears_detection_modification import ArrearsDetectionModification

router = APIRouter()


class UpdateDetectionRequest(BaseModel):
    detection_success: bool


@router.get("/arrears/detections", response_model=dict)
async def get_arrears_detections(
    car_plate_number: Optional[str] = Query(None, description="차량 번호로 필터링"),
    detection_success: Optional[bool] = Query(None, description="탐지 성공 여부로 필터링"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    limit: int = Query(100, ge=1, le=1000, description="페이지당 항목 수 (최대 1000)"),
    current_user: User = Depends(require_nts_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    체납자 차량 탐지 알림 조회 (위치, 시간)
    국세청 관리자 전용
    페이지네이션 지원
    """
    # require_nts_admin가 이미 organization 체크를 수행하므로 중복 체크 불필요
    
    query = busan_car_db.query(ArrearsDetection)
    
    # 필터링
    if car_plate_number:
        query = query.filter(ArrearsDetection.car_plate_number.like(f"%{car_plate_number}%"))
    
    if detection_success is not None:
        query = query.filter(ArrearsDetection.detection_success == (1 if detection_success else 0))
    
    if start_date:
        query = query.filter(ArrearsDetection.detected_time >= start_date)
    
    if end_date:
        query = query.filter(ArrearsDetection.detected_time <= end_date)
    
    # 총 개수 계산 (필터링 후)
    total_count = query.count()
    
    # 페이지네이션 적용
    offset = (page - 1) * limit
    detections = query.order_by(ArrearsDetection.detected_time.desc()).offset(offset).limit(limit).all()
    
    # 총 페이지 수 계산
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    
    # 해결완료 여부 조회 (web DB)
    detection_ids = [d.detection_id for d in detections]
    resolved_detections = {}
    if detection_ids:
        resolved_records = web_db.query(ArrearsDetectionModification).filter(
            ArrearsDetectionModification.detection_id.in_(detection_ids),
            ArrearsDetectionModification.is_resolved == True
        ).all()
        resolved_detections = {r.detection_id: True for r in resolved_records}
    
    return {
        "items": [{
            "detectionId": d.detection_id,
            "carPlateNumber": d.car_plate_number or "알 수 없음",
            "imageId": d.image_id,
            "detectionSuccess": bool(d.detection_success) if d.detection_success is not None else None,
            "detectedLat": d.detected_lat,
            "detectedLon": d.detected_lon,
            "detectedTime": d.detected_time.isoformat() if d.detected_time else None,
            "location": f"위도: {d.detected_lat}, 경도: {d.detected_lon}" if d.detected_lat and d.detected_lon else "위치 정보 없음",
            "isResolved": resolved_detections.get(d.detection_id, False)
        } for d in detections],
        "total": total_count,
        "page": page,
        "limit": limit,
        "totalPages": total_pages
    }


@router.put("/arrears/detections/{detection_id}", response_model=dict)
async def update_detection_result(
    detection_id: str,
    request: UpdateDetectionRequest,
    current_user: User = Depends(require_nts_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    탐지 결과 수정 기능
    국세청 관리자 전용
    web DB에 수정 기록 저장
    """
    # require_nts_admin가 이미 organization 체크를 수행하므로 중복 체크 불필요
    
    # 탐지 기록 조회 (busan_car DB)
    detection = busan_car_db.query(ArrearsDetection).filter(
        ArrearsDetection.detection_id == detection_id
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
    
    # 기존 수정 기록 확인 (같은 car_plate_number와 detection_id)
    car_plate_number = detection.car_plate_number or "알 수 없음"
    existing_modification = web_db.query(ArrearsDetectionModification).filter(
        ArrearsDetectionModification.detection_id == detection_id,
        ArrearsDetectionModification.car_plate_number == car_plate_number
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
        modification = ArrearsDetectionModification(
            detection_id=detection_id,
            car_plate_number=car_plate_number,
            previous_result=previous_result,
            new_result=request.detection_success,
            modified_by_user_id=current_user.id
        )
        web_db.add(modification)
        web_db.commit()
        web_db.refresh(modification)
    
    return {
        "detectionId": detection.detection_id,
        "carPlateNumber": detection.car_plate_number,
        "detectionSuccess": bool(detection.detection_success),
        "message": "탐지 결과가 수정되었습니다"
    }


@router.put("/arrears/detections/{detection_id}/resolve", response_model=dict)
async def resolve_arrears(
    detection_id: str,
    current_user: User = Depends(require_nts_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    체납자 해결완료 처리
    국세청 관리자 전용
    web DB에 해결완료 기록 저장
    """
    # 탐지 기록 조회 (busan_car DB)
    detection = busan_car_db.query(ArrearsDetection).filter(
        ArrearsDetection.detection_id == detection_id
    ).first()
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="탐지 기록을 찾을 수 없습니다"
        )
    
    car_plate_number = detection.car_plate_number or "알 수 없음"
    
    # 기존 수정 기록 확인 (같은 car_plate_number와 detection_id)
    existing_modification = web_db.query(ArrearsDetectionModification).filter(
        ArrearsDetectionModification.detection_id == detection_id,
        ArrearsDetectionModification.car_plate_number == car_plate_number
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
        resolution = ArrearsDetectionModification(
            detection_id=detection_id,
            car_plate_number=car_plate_number,
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
        "carPlateNumber": detection.car_plate_number,
        "isResolved": True,
        "resolvedAt": resolution.resolved_at.isoformat() if resolution.resolved_at else None,
        "message": "해결완료 처리되었습니다"
    }


@router.get("/arrears/detections/recent", response_model=List[dict])
async def get_recent_detections(
    since: Optional[datetime] = Query(None, description="이 시간 이후의 탐지 기록 조회"),
    current_user: User = Depends(require_nts_admin),
    db: Session = Depends(get_busan_car_db)
):
    """
    최신 탐지 기록 조회 (알림용)
    국세청 관리자 전용
    특정 시간 이후의 새로운 탐지 기록만 반환
    """
    # require_nts_admin가 이미 organization 체크를 수행하므로 중복 체크 불필요
    
    query = db.query(ArrearsDetection)
    
    # 특정 시간 이후의 탐지 기록만 조회
    if since:
        query = query.filter(ArrearsDetection.detected_time > since)
    
    # 최신순 정렬, 최대 50개만 반환 (알림용이므로)
    detections = query.order_by(ArrearsDetection.detected_time.desc()).limit(50).all()
    
    return [{
        "detectionId": d.detection_id,
        "carPlateNumber": d.car_plate_number or "알 수 없음",
        "detectionSuccess": bool(d.detection_success) if d.detection_success is not None else None,
        "detectedLat": d.detected_lat,
        "detectedLon": d.detected_lon,
        "detectedTime": d.detected_time.isoformat() if d.detected_time else None,
        "location": f"위도: {d.detected_lat}, 경도: {d.detected_lon}" if d.detected_lat and d.detected_lon else "위치 정보 없음"
    } for d in detections]


@router.get("/arrears/stats", response_model=dict)
async def get_arrears_stats(
    current_user: User = Depends(require_nts_admin),
    busan_car_db: Session = Depends(get_busan_car_db),
    web_db: Session = Depends(get_web_db)
):
    """
    체납자 통계 조회
    - 전체 체납자 수 (arrears_info 테이블)
    - 탐지 성공 건수 (arrears_detection에서 detection_success = 1)
    - 탐지 실패 건수 (전체 체납자 - 탐지 성공)
    - 미확인 건수 (arrears_detection에서 detection_success = NULL)
    """
    # require_nts_admin가 이미 organization 체크를 수행하므로 중복 체크 불필요
    
    # 전체 체납자 수 (arrears_info 테이블)
    total_arrears = busan_car_db.query(func.count(ArrearsInfo.car_plate_number)).scalar() or 0
    
    # 탐지 성공 건수 (arrears_detection에서 detection_success = 1)
    success_count = busan_car_db.query(func.count(ArrearsDetection.detection_id)).filter(
        ArrearsDetection.detection_success == 1
    ).scalar() or 0
    
    # 미탐지 건수 = 전체 체납자 - 탐지 성공
    undetected_count = total_arrears - success_count
    
    # 미확인 건수 (arrears_detection에서 detection_success = NULL)
    unconfirmed_count = busan_car_db.query(func.count(ArrearsDetection.detection_id)).filter(
        ArrearsDetection.detection_success.is_(None)
    ).scalar() or 0
    
    # 오탐지로 수정한 횟수 (new_result = 0인 것의 개수)
    false_positive_count = web_db.query(func.count(ArrearsDetectionModification.id)).filter(
        ArrearsDetectionModification.new_result == False
    ).scalar() or 0
    
    # 해결완료 건수 (web DB에서 is_resolved = True인 것)
    now = datetime.now()
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
    
    return {
        "totalArrears": total_arrears,
        "detectionSuccess": success_count,
        "undetected": undetected_count,  # 미탐지 (전체 체납자 - 탐지 성공)
        "falsePositiveCount": false_positive_count,  # 오탐지로 수정한 횟수
        "unconfirmed": unconfirmed_count,
        "resolvedCount": resolved_count
    }

