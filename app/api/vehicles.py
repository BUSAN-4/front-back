from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleType
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse

router = APIRouter()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle: VehicleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """차량 등록"""
    # Pydantic 모델을 dict로 변환 (by_alias=False로 필드명 사용)
    vehicle_dict = vehicle.dict(by_alias=False)
    
    # 중복 확인
    existing = db.query(Vehicle).filter(Vehicle.license_plate == vehicle_dict.get("licensePlate")).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this license plate already exists"
        )
    
    # vehicle_type을 enum으로 변환
    vehicle_type_enum = VehicleType(vehicle_dict.get("vehicleType"))
    
    db_vehicle = Vehicle(
        license_plate=vehicle_dict.get("licensePlate"),
        vehicle_type=vehicle_type_enum,
        model=vehicle_dict.get("model"),
        year=vehicle_dict.get("year"),
        user_id=current_user.id
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    vehicle_response = VehicleResponse.from_orm_vehicle(db_vehicle)
    return vehicle_response.dict()


@router.get("", response_model=List[dict])
async def get_vehicles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자의 차량 목록 조회"""
    vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user.id).all()
    return [VehicleResponse.from_orm_vehicle(v).dict() for v in vehicles]


@router.get("/{vehicle_id}", response_model=dict)
async def get_vehicle(
    vehicle_id: str,  # frontend는 string으로 전달
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """차량 상세 조회"""
    try:
        vehicle_id_int = int(vehicle_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle ID"
        )
    """차량 상세 조회"""
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id_int,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle_response = VehicleResponse.from_orm_vehicle(vehicle)
    return vehicle_response.dict()


@router.put("/{vehicle_id}", response_model=dict)
async def update_vehicle(
    vehicle_id: str,  # frontend는 string으로 전달
    vehicle_update: VehicleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """차량 정보 수정"""
    try:
        vehicle_id_int = int(vehicle_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle ID"
        )
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id_int,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    update_data = vehicle_update.dict(exclude_unset=True, by_alias=True)
    
    # licensePlate 중복 확인
    if "licensePlate" in update_data and update_data["licensePlate"] != vehicle.license_plate:
        existing = db.query(Vehicle).filter(
            Vehicle.license_plate == update_data["licensePlate"],
            Vehicle.id != vehicle_id_int
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this license plate already exists"
            )
        vehicle.license_plate = update_data["licensePlate"]
    
    if "vehicleType" in update_data:
        vehicle.vehicle_type = VehicleType(update_data["vehicleType"])
    if "model" in update_data:
        vehicle.model = update_data["model"]
    if "year" in update_data:
        vehicle.year = update_data["year"]
    
    db.commit()
    db.refresh(vehicle)
    
    vehicle_response = VehicleResponse.from_orm_vehicle(vehicle)
    return vehicle_response.dict()


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: str,  # frontend는 string으로 전달
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """차량 삭제"""
    try:
        vehicle_id_int = int(vehicle_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid vehicle ID"
        )
    
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id_int,
        Vehicle.user_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    db.delete(vehicle)
    db.commit()
    return None

