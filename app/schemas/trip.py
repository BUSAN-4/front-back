from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TripBase(BaseModel):
    start_time: datetime
    end_time: datetime
    distance: float  # km
    duration: int  # 초 단위
    safety_score: Optional[float] = None
    drowsiness_count: int = 0
    sudden_acceleration_count: int = 0
    location: Optional[str] = None


class TripCreate(TripBase):
    vehicle_id: int


class TripResponse(BaseModel):
    id: str  # frontend는 string으로 사용
    vehicleId: str  # frontend는 string으로 사용
    startTime: str  # ISO format string
    endTime: str  # ISO format string
    distance: float
    duration: int
    safetyScore: Optional[float] = None
    drowsinessCount: int = 0
    suddenAccelerationCount: int = 0
    location: Optional[str] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_trip(cls, trip):
        """ORM Trip 객체를 TripResponse로 변환"""
        return cls(
            id=str(trip.id),
            vehicleId=str(trip.vehicle_id),
            startTime=trip.start_time.isoformat() if trip.start_time else "",
            endTime=trip.end_time.isoformat() if trip.end_time else "",
            distance=trip.distance,
            duration=trip.duration,
            safetyScore=trip.safety_score,
            drowsinessCount=trip.drowsiness_count,
            suddenAccelerationCount=trip.sudden_acceleration_count,
            location=trip.location
        )

