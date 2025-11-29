from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ViolationType(str, enum.Enum):
    ILLEGAL_PARKING = "illegal_parking"
    SPEEDING = "speeding"
    RED_LIGHT = "red_light"
    OTHER = "other"


class ViolationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    PAID = "paid"


class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    violation_type = Column(Enum(ViolationType), nullable=False)
    location = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    violation_time = Column(DateTime(timezone=True))
    fine_amount = Column(Integer)
    status = Column(Enum(ViolationStatus), default=ViolationStatus.PENDING)
    description = Column(Text)
    image_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    vehicle = relationship("Vehicle")

