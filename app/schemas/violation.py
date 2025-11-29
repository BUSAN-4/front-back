from pydantic import BaseModel
from datetime import datetime
from app.models.violation import ViolationType, ViolationStatus


class ViolationBase(BaseModel):
    violation_type: ViolationType
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    violation_time: datetime | None = None
    fine_amount: int | None = None
    description: str | None = None
    image_url: str | None = None


class ViolationCreate(ViolationBase):
    vehicle_id: int


class ViolationUpdate(BaseModel):
    status: ViolationStatus | None = None
    fine_amount: int | None = None
    description: str | None = None


class ViolationResponse(ViolationBase):
    id: int
    vehicle_id: int
    status: ViolationStatus
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

