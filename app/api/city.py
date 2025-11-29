from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import require_city_admin
from app.models.user import User
from app.models.violation import Violation
from app.schemas.violation import ViolationResponse, ViolationUpdate

router = APIRouter()


@router.get("/violations", response_model=List[ViolationResponse])
async def get_violations(
    current_user: User = Depends(require_city_admin),
    db: Session = Depends(get_db)
):
    """불법주정차 등 위반 사항 조회 (시청 관리자)"""
    violations = db.query(Violation).order_by(Violation.created_at.desc()).all()
    return violations


@router.put("/violations/{violation_id}", response_model=ViolationResponse)
async def update_violation(
    violation_id: int,
    violation_update: ViolationUpdate,
    current_user: User = Depends(require_city_admin),
    db: Session = Depends(get_db)
):
    """위반 사항 상태 업데이트 (시청 관리자)"""
    violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if not violation:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Violation not found"
        )
    
    update_data = violation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(violation, field, value)
    
    db.commit()
    db.refresh(violation)
    return violation

