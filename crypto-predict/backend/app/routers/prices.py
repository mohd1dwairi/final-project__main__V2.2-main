from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db import models
# استيراد محرك التوقع الذي يعالج ملفات الـ .pt و .json
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

# 2. مسار التوقع الحقيقي (AI Hybrid Prediction)
@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    try:
        # أ. جلب آخر 48 ساعة من البيانات (SEQ_LEN = 48)
        candles = db.query(models.Candle).filter(
            models.Candle.asset == symbol.lower()
        ).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(candles) < 48:
            raise HTTPException(status_code=400, detail="بيانات غير كافية (نحتاج 48 ساعة من البيانات التاريخية)")

        # ب. تحويل بيانات الشموع إلى DataFrame وترتيبها زمنياً (تصاعدي)
        df_input = pd.DataFrame([
            {
                "timestamp": c.timestamp,
                "open": c.open, "high": c.high, "low": c.low, "close": c.close, "volume": c.volume
            } for c in candles
        ]).sort_values("timestamp")

        # ج. دمج بيانات المشاعر (Sentiment) لضمان الـ 14 خاصية
        sentiments = db.query(models.Sentiment).filter(
            models.Sentiment.asset == symbol.lower(),
            models.Sentiment.timestamp.in_(df_input["timestamp"].tolist())
        ).all()
        
        sent_dict = {s.timestamp: s for s in sentiments}
        
        # تعريف الأعمدة المطلوبة بالترتيب الصحيح للموديل
        feature_cols = [
            "open", "high", "low", "close", "volume", 
            "sent_count", "avg_sentiment", "pos_count", "neg_count", "neu_count", 
            "pos_ratio", "neg_ratio", "neu_ratio", "has_news"
        ]

        # تعبئة بيانات المشاعر برمجياً
        for col in feature_cols[5:]: # تبدأ من sent_count
            df_input[col] = df_input["timestamp"].apply(
                lambda x: getattr(sent_dict[x], "score") if (x in sent_dict and col == "avg_sentiment") else 
                          (sent_dict[x].meta.get(col, 0) if (x in sent_dict and isinstance(sent_dict[x].meta, dict)) else 0.0)
            )

        # د. تنفيذ التوقع عبر المحرك الهجين
        # نرسل الأعمدة بالترتيب الدقيق الذي يطلبه الموديل
        prediction = inference_engine.predict(df_input[feature_cols])

        # هـ. تجهيز النتيجة لـ 5 ساعات قادمة للرسم البياني
        future_results = []
        last_price = df_input["close"].iloc[-1]
        
        for i in range(1, 6):
            # حساب القيمة المتوقعة بناءً على العائد (Return)
            # تم تقسيم العائد على 5 لتوزيعه كصعود تدريجي في الرسم البياني
            predicted_val = last_price * (1 + (prediction["predicted_return"] * i / 5))
            
            future_results.append({
                "timestamp": (datetime.now() + timedelta(hours=i)).isoformat(),
                "predicted_value": round(predicted_val, 2),
                "trend": prediction["trend"],
                "confidence": prediction["confidence"]
            })

        return future_results

    except Exception as e:
        # طباعة الخطأ في الـ Logs لتسهيل تتبعه
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