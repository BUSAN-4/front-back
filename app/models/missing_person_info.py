from sqlalchemy import Column, String, Integer, DateTime
from app.database import BusanCarBase


class MissingPersonInfo(BusanCarBase):
    """missing_person_info 테이블 모델 (읽기 전용)"""
    __tablename__ = "missing_person_info"
    __table_args__ = {'schema': None}
    
    missing_id = Column(String(64), primary_key=True, index=True)
    missing_name = Column(String(100))
    missing_age = Column(Integer)
    missing_identity = Column(String(255))
    registered_at = Column(DateTime)
    updated_at = Column(DateTime)
    missing_location = Column(String(50))

