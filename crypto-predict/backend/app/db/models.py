from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, JSON, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from datetime import date
from app.db.session import Base

# 1. Users Table (Renamed to 'users' to avoid Postgres reserved word issues)
class User(Base):
    __tablename__ = "users" 
    
    user_id = Column(Integer, primary_key=True, index=True) 
    User_Name = Column(String(50), nullable=False) 
    email = Column(String(255), unique=True, nullable=False, index=True) 
    password_hash = Column(String(255), nullable=False) 
    created_at = Column(Date, default=date.today) 

    predictions = relationship("Prediction", back_populates="creator")

# 2. Historical Price Data (OHLCV)
class Candle(Base):
    __tablename__ = "candle_ohlcv"

    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False)
    exchange = Column(String(30), default="binance")
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("asset", "exchange", "timestamp", name="uq_candle_asset_exch_ts"),
        Index("ix_candle_asset_ts", "asset", "timestamp"),
    )

# 3. Prediction Table
class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_price = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    creator = relationship("User", back_populates="predictions")

# 4. Model Registry Table
class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    path = Column(String(255))
    params = Column(JSON)
    metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_model_name_version"),
    )