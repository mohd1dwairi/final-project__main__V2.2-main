from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db import models
# استيراد محرك التوقع
from app.services.inference_service import inference_engine

router = APIRouter(prefix="/prices", tags=["Prices"])

# 1. مسار البطاقات العلوية
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

# 2. مسار التوقع الحقيقي (AI Hybrid Prediction) - النسخة المصححة
@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    try:
        # أ. جلب آخر 48 ساعة من البيانات المدمجة (Join بين الأسعار والمشاعر)
        # نستخدم الـ Join هنا لضمان الحصول على الساعات التي تحتوي على سعر ومشاعر معاً
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
                detail=f"بيانات غير كافية لـ {symbol}. نحتاج 48 ساعة مدمجة (سعر + مشاعر) في القاعدة."
            )

        # ب. تجهيز الـ 14 خاصية المطلوبة للموديل بالترتيب الصحيح
        feature_data = []
        for candle, sentiment in query_results:
            feature_data.append({
                "timestamp": candle.timestamp,
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                # الوصول المباشر للأعمدة الجديدة بدلاً من .meta
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
        
        # تحويل لـ DataFrame والترتيب زمنياً (تصاعدي)
        df_input = pd.DataFrame(feature_data).sort_values("timestamp")

        # تعريف ترتيب الأعمدة الدقيق للموديل
        feature_cols = [
            "open", "high", "low", "close", "volume", 
            "sent_count", "avg_sentiment", "pos_count", "neg_count", "neu_count", 
            "pos_ratio", "neg_ratio", "neu_ratio", "has_news"
        ]

        # ج. تنفيذ التوقع عبر المحرك الهجين
        prediction = inference_engine.predict(df_input[feature_cols])

        # د. تجهيز النتيجة لـ 5 ساعات قادمة للرسم البياني
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
        print(f"Prediction Error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")

# 3. مسار الشمعات التاريخية (ApexCharts)
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    data = db.query(models.Candle).filter(
        models.Candle.asset == symbol.lower()
    ).order_by(models.Candle.timestamp.desc()).limit(100).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="العملة غير موجودة")

    return sorted([
        {
            "x": c.timestamp,
            "y": [c.open, c.high, c.low, c.close]
        } for c in data
    ], key=lambda x: x['x'])