"""
실종자 탐지 결과 수정 기록 모델 (web DB)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MissingPersonDetectionModification(Base):
    """실종자 탐지 결과 수정 기록 테이블"""
    __tablename__ = "missing_person_detection_modifications"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(String(64), nullable=False, index=True)  # busan_car.missing_person_detection의 detection_id
    missing_id = Column(String(64), nullable=False, index=True)  # 실종자 ID
    previous_result = Column(Boolean, nullable=True)  # 이전 탐지 결과 (NULL, True, False)
    new_result = Column(Boolean, nullable=False)  # 새로운 탐지 결과 (True: 탐지 성공, False: 탐지 실패)
    modified_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 수정한 사용자 ID
    modification_reason = Column(String(500), nullable=True)  # 수정 사유 (선택)
    is_resolved = Column(Boolean, nullable=False, default=False, index=True)  # 해결완료 여부
    resolved_at = Column(DateTime(timezone=True), nullable=True, index=True)  # 해결완료 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 관계
    modifier = relationship("User", backref="missing_person_modifications")


