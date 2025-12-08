from sqlalchemy import Column, String, Integer, DateTime
from app.database import Base


class UserVehicle(Base):
    """uservehicle 테이블 모델"""
    __tablename__ = "uservehicle"
    
    car_id = Column(String(255), primary_key=True, index=True)
    age = Column(Integer)
    user_sex = Column(String(10))  # enum('남','여')
    user_location = Column(String(255))
    user_car_class = Column(String(255))
    user_car_brand = Column(String(255))
    user_car_year = Column(Integer)
    user_car_model = Column(String(255))
    user_car_weight = Column(Integer)
    user_car_displace = Column(Integer)
    user_car_efficiency = Column(String(255))
    updated_at = Column(DateTime)







