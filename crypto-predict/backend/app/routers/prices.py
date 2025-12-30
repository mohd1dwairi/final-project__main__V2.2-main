from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/prices", tags=["Prices"])

# 1. مسار البطاقات العلوية (يجب أن يكون في البداية)
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

# 2. مسار التوقعات (مؤسس لربط الذكاء الاصطناعي لاحقاً)
@router.get("/predict/{symbol}")
def get_predictions(symbol: str, db: Session = Depends(get_db)):
    last_candle = db.query(models.Candle).filter(
        models.Candle.asset == symbol.lower()
    ).order_by(models.Candle.timestamp.desc()).first()

    if not last_candle: return []

    predictions = []
    current_time = last_candle.timestamp
    for i in range(1, 6):
        future_time = current_time + timedelta(hours=i)
        predictions.append({
            "timestamp": future_time,
            "predicted_value": round(last_candle.close * (1 + (i * 0.005)), 2),
            "trend": "Up" if i % 2 == 0 else "Steady",
            "confidence": f"{90 - i}%"
        })
    return predictions

# 3. مسار الشمعات التاريخية (Open, High, Low, Close)
@router.get("/{symbol}")
def get_historical_ohlcv(symbol: str, db: Session = Depends(get_db)):
    data = db.query(models.Candle).filter(
        models.Candle.asset == symbol.lower()
    ).order_by(models.Candle.timestamp.desc()).limit(100).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="Coin not found")

    # تنسيق خاص بـ ApexCharts للشمعات: [وقت، فتح، أعلى، أدنى، إغلاق]
    return sorted([
        {
            "x": c.timestamp,
            "y": [c.open, c.high, c.low, c.close]
        } for c in data
    ], key=lambda x: x['x'])