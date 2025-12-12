from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class DrivingSession(Base):
    """driving_session 테이블 모델"""
    __tablename__ = "driving_session"
    
    session_id = Column(String(255), primary_key=True, index=True)
    car_id = Column(String(255), index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())













