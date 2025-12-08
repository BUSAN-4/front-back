from sqlalchemy import Column, String, Integer, Float, DateTime
from app.database import Base


class ArrearsDetection(Base):
    """arrears_detection 테이블 모델"""
    __tablename__ = "arrears_detection"
    
    detection_id = Column(String(64), primary_key=True, index=True)
    car_plate_number = Column(String(20), index=True)
    image_id = Column(String(64))
    detection_success = Column(Integer)  # tinyint(1)
    detected_lat = Column(Float)
    detected_lon = Column(Float)
    detected_time = Column(DateTime)







