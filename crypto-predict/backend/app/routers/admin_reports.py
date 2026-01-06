from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin Reports"])

# ==========================================
# 1. إحصائيات النظام (الأسهل)
# ==========================================
@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """
    جلب الأرقام الكلية من قاعدة البيانات لإعطاء نظرة عامة للأدمن.
    """
    total_users = db.query(func.count(models.User.user_id)).scalar()
    total_records = db.query(func.count(models.Candle.iid)).scalar()
    total_predictions = db.query(func.count(models.Prediction.id)).scalar()
    
    return {
        "users_count": total_users,
        "data_records": total_records,
        "predictions_made": total_predictions
    }

# ==========================================
# 2. تقرير دقة التوقع (متوسط الصعوبة - Backtesting)
# ==========================================
@router.get("/accuracy-report/{symbol}")
def get_accuracy_report(symbol: str, db: Session = Depends(get_db)):
    """
    مقارنة التوقعات السابقة بالأسعار الحقيقية المخزنة في candle_ohlcv.
    """
    target = symbol.lower()
    
    # دمج جدول التوقعات مع جدول الأسعار الحقيقية بناءً على الوقت والعملة
    comparison = db.query(
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price")
    ).join(
        models.Candle, 
        (models.Prediction.asset == models.Candle.asset) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).filter(models.Prediction.asset == target).limit(50).all()

    report_data = []
    for row in comparison:
        error = abs(row.predicted_price - row.actual_price)
        accuracy = 100 - ((error / row.actual_price) * 100)
        report_data.append({
            "time": row.timestamp,
            "predicted": row.predicted_price,
            "actual": row.actual_price,
            "accuracy": round(accuracy, 2)
        })
        
    return report_data