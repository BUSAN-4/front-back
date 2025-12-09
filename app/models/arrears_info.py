from sqlalchemy import Column, String, Integer, DateTime
from app.database import BusanCarBase


class ArrearsInfo(BusanCarBase):
    """arrears_info 테이블 모델 (읽기 전용)"""
    __tablename__ = "arrears_info"
    __table_args__ = {'schema': None}
    
    car_plate_number = Column(String(20), primary_key=True, index=True)
    arrears_user_id = Column(String(64))
    total_arrears_amount = Column(Integer)
    arrears_period = Column(String(50))
    notice_sent = Column(Integer)  # tinyint(1)
    updated_at = Column(DateTime)

