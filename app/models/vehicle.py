from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class VehicleType(str, enum.Enum):
    PRIVATE = "private"
    TAXI = "taxi"
    RENTAL = "rental"


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    model = Column(String(50))
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계
    user = relationship("User", back_populates="vehicles")
    trips = relationship("Trip", back_populates="vehicle")

