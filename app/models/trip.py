from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    distance = Column(Float, nullable=False)  # km
    duration = Column(Integer, nullable=False)  # 초 단위
    safety_score = Column(Float)  # 안전 점수
    drowsiness_count = Column(Integer, default=0)  # 졸음 운전 횟수
    sudden_acceleration_count = Column(Integer, default=0)  # 급가속 횟수
    location = Column(String(255))  # 위치 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    vehicle = relationship("Vehicle", back_populates="trips")

