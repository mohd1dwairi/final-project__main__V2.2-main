from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import datetime, timedelta
from pydantic import BaseModel

# استيراد إعدادات قاعدة البيانات والموديلات
from app.db.session import get_db
from app.db import models
# استيراد محرك التوقع (AI Engine)
from app.services.inference_service import inference_engine

router = APIRouter(prefix="/prices", tags=["Prices"])

# ==========================================
# 1. تعريف شكل البيانات المدخلة (Schemas)
# وضعناه في الأعلى ليتم التعرف عليه من قبل جميع الدوال بالأسفل
# ==========================================
class MarketDataInput(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    avg_sentiment: float
    sent_count: int = 0
    pos_count: int = 0
    neg_count: int = 0
    neu_count: int = 0
    pos_ratio: float = 0.0
    neg_ratio: float = 0.0
    neu_ratio: float = 0.0
    has_news: int = 0

# ==========================================
# 2. المسارات السهلة (GET)
# ==========================================

# مسار البطاقات العلوية (أحدث أسعار العملات)
@router.get("/top-assets")
def get_top_assets(db: Session = Depends(get_db)):
    subquery = db.query(
        models.Candle.asset,
        func.max(models.Candle.timestamp).label("max_ts")
    ).group_by(models.Candle.asset).subquery()

    latest_prices = db.query(models.Candle).join(
        subquery, (models.Candle.asset == subquery.c.asset) & (models.Candle.timestamp == subquery.c.max_ts)
    ).all()

    return [
        {"id": p.asset.upper(), "name": p.asset.upper(), "price": p.close, "change": 0.5} 
        for p in latest_prices
    ]

# مسار الشمعات التاريخية (لعرض الرسم البياني التاريخي OHLC)
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    data = db.query(models.Candle).filter(
        models.Candle.asset == symbol.lower()
    ).order_by(models.Candle.timestamp.desc()).limit(100).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="العملة غير موجودة في قاعدة البيانات")

    return sorted([
        {
            "x": c.timestamp,
            "y": [c.open, c.high, c.low, c.close]
        } for c in data
    ], key=lambda x: x['x'])

# ==========================================
# 3. مسار إضافة البيانات (POST)
# ==========================================

# مسار يسمح للمستخدم (أو النظام) بإضافة سجل جديد يدوياً
@router.post("/add-data")
def add_market_data(data: MarketDataInput, db: Session = Depends(get_db)):
    try:
        now_ts = datetime.now()
        
        # إضافة سجل السعر
        new_candle = models.Candle(
            asset=data.symbol.lower(),
            timestamp=now_ts,
            open=data.open, high=data.high, low=data.low,
            close=data.close, volume=data.volume
        )
        
        # إضافة سجل المشاعر (Sentiment)
        new_sentiment = models.Sentiment(
            asset=data.symbol.lower(),
            timestamp=now_ts,
            avg_sentiment=data.avg_sentiment,
            sent_count=data.sent_count,
            pos_count=data.pos_count,
            neg_count=data.neg_count,
            neu_count=data.neu_count,
            pos_ratio=data.pos_ratio,
            neg_ratio=data.neg_ratio,
            neu_ratio=data.neu_ratio,
            has_news=data.has_news
        )
        
        db.add(new_candle)
        db.add(new_sentiment)
        db.commit()
        
        return {"status": "success", "message": f"New record added for {data.symbol} at {now_ts}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# ==========================================
# 4. مسار التوقع المعقد (AI Predict)
# ==========================================

@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    try:
        # جلب آخر 48 ساعة من البيانات المدمجة (Join سريع)
        query_results = db.query(models.Candle, models.Sentiment).join(
            models.Sentiment, 
            (models.Candle.asset == models.Sentiment.asset) & 
            (models.Candle.timestamp == models.Sentiment.timestamp)
        ).filter(
            models.Candle.asset == symbol.lower()
        ).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(query_results) < 48:
            raise HTTPException(
                status_code=400, 
                detail=f"بيانات غير كافية لـ {symbol}. نحتاج 48 ساعة مدمجة (سعر + مشاعر) لإجراء التوقع."
            )

        # تجهيز البيانات للموديل
        feature_data = []
        for candle, sentiment in query_results:
            feature_data.append({
                "timestamp": candle.timestamp,
                "open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close, "volume": candle.volume,
                "sent_count": sentiment.sent_count,
                "avg_sentiment": sentiment.avg_sentiment,
                "pos_count": sentiment.pos_count,
                "neg_count": sentiment.neg_count,
                "neu_count": sentiment.neu_count,
                "pos_ratio": sentiment.pos_ratio,
                "neg_ratio": sentiment.neg_ratio,
                "neu_ratio": sentiment.neu_ratio,
                "has_news": sentiment.has_news
            })
        
        # تحويل لـ DataFrame وترتيب زمنياً
        df_input = pd.DataFrame(feature_data).sort_values("timestamp")

        # ترتيب الأعمدة الـ 14 الدقيق
        feature_cols = [
            "open", "high", "low", "close", "volume", 
            "sent_count", "avg_sentiment", "pos_count", "neg_count", "neu_count", 
            "pos_ratio", "neg_ratio", "neu_ratio", "has_news"
        ]

        # تنفيذ التوقع
        prediction = inference_engine.predict(df_input[feature_cols])

        # تجهيز نتائج الرسم البياني المستقبلي
        future_results = []
        last_price = df_input["close"].iloc[-1]
        
        for i in range(1, 6):
            predicted_val = last_price * (1 + (prediction["predicted_return"] * i / 5))
            future_results.append({
                "timestamp": (datetime.now() + timedelta(hours=i)).isoformat(),
                "predicted_value": round(predicted_val, 2),
                "trend": prediction["trend"],
                "confidence": prediction["confidence"]
            })

        return future_results

    except Exception as e:
        print(f"Prediction Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")