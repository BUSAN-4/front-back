"""
체납 차량 탐지 결과 수정 기록 모델 (web DB)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ArrearsDetectionModification(Base):
    """체납 차량 탐지 결과 수정 기록 테이블"""
    __tablename__ = "arrears_detection_modifications"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(64), nullable=False, index=True)  # busan_car.arrears_detection의 detection_id
    car_plate_number = Column(String(20), nullable=False, index=True)  # 차량 번호판
    previous_result = Column(Boolean, nullable=True)  # 이전 탐지 결과 (NULL, True, False)
    new_result = Column(Boolean, nullable=False)  # 새로운 탐지 결과 (True: 탐지 성공, False: 미탐지)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 수정한 사용자 ID
    modification_reason = Column(String(500), nullable=True)  # 수정 사유 (선택)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)  # 해결완료 여부
    resolved_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 해결완료 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 관계
    modifier = relationship("User", backref="arrears_modifications")


