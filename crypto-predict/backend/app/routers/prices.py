from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import io
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
# 2. المسارات السهلة (GET) - جلب البيانات التاريخية والإحصائيات
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
    target_asset = symbol.lower()
    data = db.query(models.Candle).filter(
        models.Candle.asset == target_asset
    ).order_by(models.Candle.timestamp.desc()).limit(150).all()
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol} in candle_ohlcv table.")

    return sorted([
        {"x": c.timestamp, "y": [c.open, c.high, c.low, c.close]} for c in data
    ], key=lambda x: x['x'])

# ==========================================
# 3. مسارات الإدارة (Admin) - الرفع الجماعي والإضافة اليدوية
# ==========================================

# ميزة جديدة: الرفع الجماعي عبر ملف CSV
@router.post("/upload-csv")
async def upload_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    هذا المسار مخصص للأدمن لرفع آلاف السجلات التاريخية دفعة واحدة.
    يقوم بمعالجة الملف باستخدام Pandas وحفظه في قاعدة البيانات بكفاءة عالية.
    """
    try:
        # قراءة محتوى الملف المرفوع وتحويله إلى DataFrame
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # التحقق من وجود الأعمدة السبعة الأساسية المطلوبة للشموع
        required_cols = ['asset', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail="The CSV file is missing required columns.")

        # تحويل البيانات إلى كائنات SQLAlchemy (Bulk Mapping)
        new_candles = []
        for _, row in df.iterrows():
            new_candles.append(models.Candle(
                asset=str(row['asset']).lower(),
                timestamp=pd.to_datetime(row['timestamp']),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume'])
            ))

        # استخدام bulk_save_objects لتسريع عملية الحفظ في قاعدة البيانات
        db.bulk_save_objects(new_candles)
        db.commit()

        return {"status": "success", "message": f"Successfully imported {len(new_candles)} records."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk Import Error: {str(e)}")

# مسار إضافة سجل واحد يدوياً (للمحاكاة)
@router.post("/add-data")
def add_market_data(data: MarketDataInput, db: Session = Depends(get_db)):
    try:
        now_ts = datetime.now()
        new_candle = models.Candle(
            asset=data.symbol.lower(), timestamp=now_ts,
            open=data.open, high=data.high, low=data.low,
            close=data.close, volume=data.volume
        )
        new_sentiment = models.Sentiment(
            asset=data.symbol.lower(), timestamp=now_ts,
            avg_sentiment=data.avg_sentiment, sent_count=data.sent_count,
            pos_count=data.pos_count, neg_count=data.neg_count, neu_count=data.neu_count,
            pos_ratio=data.pos_ratio, neg_ratio=data.neg_ratio, neu_ratio=data.neu_ratio,
            has_news=data.has_news
        )
        db.add(new_candle); db.add(new_sentiment)
        db.commit()
        return {"status": "success", "message": f"New record added for {data.symbol}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

# ==========================================
# 4. مسار التوقع المتقدم (AI Predict)
# ==========================================

@router.get("/predict/{symbol}")
def get_ai_prediction(symbol: str, db: Session = Depends(get_db)):
    try:
        target_asset = symbol.lower()
        query_results = db.query(models.Candle, models.Sentiment).join(
            models.Sentiment, 
            (models.Candle.asset == models.Sentiment.asset) & 
            (models.Candle.timestamp == models.Sentiment.timestamp)
        ).filter(models.Candle.asset == target_asset).order_by(models.Candle.timestamp.desc()).limit(48).all()

        if len(query_results) < 48:
            raise HTTPException(status_code=400, detail=f"Insufficient data for {symbol}.")

        feature_data = []
        for candle, sentiment in query_results:
            feature_data.append({
                "timestamp": candle.timestamp, "open": candle.open, "high": candle.high, "low": candle.low, "close": candle.close, "volume": candle.volume,
                "sent_count": sentiment.sent_count, "avg_sentiment": sentiment.avg_sentiment, "pos_count": sentiment.pos_count, "neg_count": sentiment.neg_count,
                "neu_count": sentiment.neu_count, "pos_ratio": sentiment.pos_ratio, "neg_ratio": sentiment.neg_ratio, "neu_ratio": sentiment.neu_ratio, "has_news": sentiment.has_news
            })
        
        df_input = pd.DataFrame(feature_data).sort_values("timestamp")
        feature_cols = ["open", "high", "low", "close", "volume", "sent_count", "avg_sentiment", "pos_count", "neg_count", "neu_count", "pos_ratio", "neg_ratio", "neu_ratio", "has_news"]

        prediction = inference_engine.predict(df_input[feature_cols])

        future_results = []
        last_price = df_input["close"].iloc[-1]
        for i in range(1, 6):
            predicted_val = last_price * (1 + (prediction["predicted_return"] * i / 5))
            future_results.append({
                "timestamp": (datetime.now() + timedelta(hours=i)).isoformat(),
                "predicted_value": round(predicted_val, 2), "trend": prediction["trend"], "confidence": prediction["confidence"]
            })
        return future_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Engine Error: {str(e)}")