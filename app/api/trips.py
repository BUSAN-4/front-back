from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.schemas.trip import TripResponse

router = APIRouter()


@router.get("", response_model=List[dict])
async def get_trips(
    vehicle_id: Optional[str] = Query(None, description="차량 ID로 필터링 (string)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """주행 기록 조회"""
    # 사용자의 차량만 조회
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user.id).all()
    vehicle_ids = [v.id for v in vehicles]
    
    if not vehicle_ids:
        return []
    
    query = db.query(Trip).filter(Trip.vehicle_id.in_(vehicle_ids))
    
    if vehicle_id:
        try:
            vehicle_id_int = int(vehicle_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid vehicle ID"
            )
        
        if vehicle_id_int not in vehicle_ids:
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this vehicle"
            )
        query = query.filter(Trip.vehicle_id == vehicle_id_int)
    
    if start_date:
        query = query.filter(Trip.start_time >= start_date)
    
    if end_date:
        query = query.filter(Trip.start_time <= end_date)
    
    trips = query.order_by(Trip.start_time.desc()).all()
    return [TripResponse.from_orm_trip(trip).dict() for trip in trips]


@router.get("/{trip_id}", response_model=dict)
async def get_trip(
    trip_id: str,  # frontend는 string으로 전달
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """주행 기록 상세 조회"""
    try:
        trip_id_int = int(trip_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trip ID"
        )
    
    # 사용자의 차량인지 확인
    trip = db.query(Trip).filter(Trip.id == trip_id_int).first()
    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == trip.vehicle_id,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this trip"
        )
    
    trip_response = TripResponse.from_orm_trip(trip)
    return trip_response.dict()

