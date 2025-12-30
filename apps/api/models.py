from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    qr_code = Column(String, unique=True, nullable=False, index=True)

class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    checkin_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    pumphouse = Column(String, nullable=False)  # 正常/异常
    endpoint = Column(String, nullable=False)   # 正常/异常
    hydrant = Column(String, nullable=False)     # 正常/异常
    linkage = Column(String, nullable=False)     # 正常/异常
    conclusion = Column(Text, nullable=True)     # 结论
    photo_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    location = relationship("Location", backref="work_orders")
    iot_snapshot = relationship("IoTSnapshot", back_populates="work_order", uselist=False)

class IoTSnapshot(Base):
    __tablename__ = "iot_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, unique=True)
    pressure = Column(Float, nullable=False)
    pump_running = Column(Boolean, nullable=False, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    work_order = relationship("WorkOrder", back_populates="iot_snapshot")

