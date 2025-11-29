from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum


class MissingPersonStatus(str, enum.Enum):
    MISSING = "missing"
    FOUND = "found"
    CLOSED = "closed"


class MissingPerson(Base):
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    last_seen_location = Column(String(255))
    last_seen_time = Column(DateTime(timezone=True))
    description = Column(Text)
    image_url = Column(String(500))
    contact_info = Column(String(255))
    status = Column(Enum(MissingPersonStatus), default=MissingPersonStatus.MISSING)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

