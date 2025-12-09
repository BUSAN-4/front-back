from fastapi import Request
from sqlalchemy.orm import Session
from app.models.user_log import UserLog, LogStatus
from app.models.user import User


def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 가져오기"""
    if request.client:
        return request.client.host
    return "unknown"


def log_user_action(
    db: Session,
    action: str,
    status: LogStatus = LogStatus.SUCCESS,
    user: User = None,
    username: str = None,
    ip_address: str = None,
    details: str = None
):
    """사용자 액션 로그 기록"""
    log = UserLog(
        user_id=user.id if user else None,
        username=username or (user.name if user else None),
        action=action,
        ip_address=ip_address,
        status=status,
        details=details
    )
    db.add(log)
    db.commit()




