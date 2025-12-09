from sqlalchemy import Column, String, Integer, Float, DateTime
from app.database import BusanCarBase


class MissingPersonDetection(BusanCarBase):
    """missing_person_detection 테이블 모델 (읽기 전용)"""
    __tablename__ = "missing_person_detection"
    __table_args__ = {'schema': None}
    
    detection_id = Column(String(64), primary_key=True, index=True)
    image_id = Column(String(64))
    missing_id = Column(String(64), index=True)
    detection_success = Column(Integer)  # tinyint(1)
    detected_lat = Column(Float)
    detected_lon = Column(Float)
    detected_time = Column(DateTime)








