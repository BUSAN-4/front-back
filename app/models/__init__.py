# web DB 모델들 (쓰기용)
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle, VehicleType
from app.models.user_vehicle_mapping import UserVehicleMapping
from app.models.user_log import UserLog, LogStatus
from app.models.arrears_detection_modification import ArrearsDetectionModification
from app.models.missing_person_detection_modification import MissingPersonDetectionModification

# busan_car DB 모델들 (읽기 전용)
from app.models.user_vehicle import UserVehicle
from app.models.car_plate_info import CarPlateInfo
from app.models.driving_session import DrivingSession
from app.models.driving_session_info import DrivingSessionInfo
from app.models.missing_person_detection import MissingPersonDetection
from app.models.missing_person_info import MissingPersonInfo
from app.models.drowsy_drive import DrowsyDrive
from app.models.arrears_detection import ArrearsDetection
from app.models.arrears_info import ArrearsInfo

__all__ = [
    "User",
    "UserRole",
    "Vehicle",
    "VehicleType",
    "UserVehicleMapping",
    "UserLog",
    "LogStatus",
    "ArrearsDetectionModification",
    "MissingPersonDetectionModification",
    "UserVehicle",
    "CarPlateInfo",
    "DrivingSession",
    "DrivingSessionInfo",
    "MissingPersonDetection",
    "MissingPersonInfo",
    "DrowsyDrive",
    "ArrearsDetection",
    "ArrearsInfo",
]


