from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.vehicle import VehicleType


class VehicleBase(BaseModel):
    licensePlate: str = Field(..., alias="licensePlate")
    vehicleType: str = Field(..., alias="vehicleType")  # private, taxi, rental
    model: Optional[str] = Field(None, alias="model")
    year: Optional[int] = Field(None, alias="year")
    
    class Config:
        populate_by_name = True  # alias와 필드명 모두 허용


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    licensePlate: Optional[str] = Field(None, alias="licensePlate")
    vehicleType: Optional[str] = Field(None, alias="vehicleType")
    model: Optional[str] = Field(None, alias="model")
    year: Optional[int] = Field(None, alias="year")
    
    class Config:
        populate_by_name = True


class VehicleResponse(BaseModel):
    id: str  # frontend는 string으로 사용
    userId: str  # frontend는 string으로 사용
    licensePlate: str
    vehicleType: str
    model: Optional[str] = None
    year: Optional[int] = None
    createdAt: str  # ISO format string
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_vehicle(cls, vehicle):
        """ORM Vehicle 객체를 VehicleResponse로 변환"""
        return cls(
            id=str(vehicle.id),
            userId=str(vehicle.user_id),
            licensePlate=vehicle.license_plate,
            vehicleType=vehicle.vehicle_type.value if hasattr(vehicle.vehicle_type, 'value') else vehicle.vehicle_type,
            model=vehicle.model,
            year=vehicle.year,
            createdAt=vehicle.created_at.isoformat() if vehicle.created_at else ""
        )

