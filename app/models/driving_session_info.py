from sqlalchemy import Column, String, Float, Integer, DateTime
from app.database import Base


class DrivingSessionInfo(Base):
    """driving_session_info 테이블 모델"""
    __tablename__ = "driving_session_info"
    
    info_id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    app_lat = Column(Float)
    app_lon = Column(Float)
    app_prev_lat = Column(Float)
    app_prev_lon = Column(Float)
    voltage = Column(Integer)
    d_door = Column(Integer)
    p_door = Column(Integer)
    rd_door = Column(Integer)
    rp_door = Column(Integer)
    t_door = Column(Integer)
    engine_status = Column(Integer)
    r_engine_status = Column(Integer)
    stt_alert = Column(Integer)
    el_status = Column(Integer)
    detect_shock = Column(Integer)
    remain_remote = Column(Integer)
    autodoor_use = Column(Integer)
    silence_mode = Column(Integer)
    low_voltage_alert = Column(Integer)
    low_voltage_engine = Column(Integer)
    temperature = Column(Integer)
    app_travel = Column(Integer)
    app_avg_speed = Column(Float)
    app_accel = Column(Float)
    app_gradient = Column(Float)
    app_rapid_acc = Column(Integer)
    app_rapid_deacc = Column(Integer)
    speed = Column(Float)
    createdDate = Column(DateTime)
    app_weather_status = Column(String(255))
    app_precipitation = Column(Float)
    dt = Column(DateTime)
    roadname = Column(String(50))
    treveltime = Column(Float)
    Hour = Column(Integer)













