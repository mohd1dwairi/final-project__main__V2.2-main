from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Boolean, Text, JSON, UniqueConstraint, Index, func
from sqlalchemy.orm import relationship
from datetime import date
from app.db.session import Base

# ================================================================
# 1️⃣ جدول المستخدمين (USER)
# ================================================================
class User(Base):
    __tablename__ = "USER" 
    
    # تم توحيد المسميات لتطابق الـ ERD والربط البرمجي
    user_id = Column(Integer, primary_key=True, index=True) 
    User_Name = Column(String(50), nullable=False) 
    email = Column(String(255), unique=True, nullable=False, index=True) 
    password_hash = Column(String(255), nullable=False) 
    created_at = Column(Date, default=date.today) 

    # علاقة مع التوقعات: لاحظ الربط مع back_populates
    predictions = relationship("Prediction", back_populates="creator")

    def __repr__(self):
        return f"<User id={self.user_id}, User_Name={self.User_Name!r}>"


# ================================================================
# 2️⃣ جدول بيانات الأسعار التاريخية (Candle OHLCV)
# ================================================================
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


# ================================================================
# 3️⃣ جدول إشارات المشاعر (Sentiment Signal)
# ================================================================
class Sentiment(Base):
    __tablename__ = "sentiment_signal"

    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    score = Column(Float, nullable=False)
    label = Column(String(10), nullable=False)
    source = Column(String(50), nullable=False)
    source_url = Column(String(255))
    meta = Column(JSON) # تم التأكد من استيراد JSON

    __table_args__ = (
        Index("ix_sentiment_asset_ts", "asset", "timestamp"),
    )


# ================================================================
# 4️⃣ جدول التنبؤات (Prediction)
# ================================================================
class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    asset = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    predicted_price = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # تم التأكد من استيراد func

    # تصحيح الربط: الجدول اسمه "USER" والحقل "user_id"
    created_by_user_id = Column(Integer, ForeignKey("USER.user_id"))
    creator = relationship("User", back_populates="predictions")

    __table_args__ = (
        Index("ix_prediction_asset_ts", "asset", "timestamp"),
    )


# ================================================================
# 5️⃣ جدول سجل النماذج الذكية (Model Registry)
# ================================================================
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