from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db import models
from app.services.trainer import retrain_model_logic # تأكد من إنشاء هذا الملف

# تعريف الراوتر ببادئة واحدة لجميع عمليات الأدمن
router = APIRouter(prefix="/admin", tags=["Admin Operations"])

# ==========================================
# 1. تقارير الدقة (Accuracy Reports) - [سهل]
# ==========================================
@router.get("/accuracy-report")
def get_accuracy_report(db: Session = Depends(get_db)):
    """
    يقوم بربط التوقعات بالأسعار الحقيقية وحساب نسبة النجاح.
    مثالي لعرض جودة النظام أمام لجنة المناقشة.
    """
    query_results = db.query(
        models.Prediction.asset,
        models.Prediction.timestamp,
        models.Prediction.predicted_price,
        models.Candle.close.label("actual_price")
    ).join(
        models.Candle, 
        (models.Prediction.asset == models.Candle.asset) & 
        (models.Prediction.timestamp == models.Candle.timestamp)
    ).order_by(models.Prediction.timestamp.desc()).limit(20).all()

    report_data = []
    for row in query_results:
        error = abs(row.actual_price - row.predicted_price)
        accuracy_val = 100 - ((error / row.actual_price) * 100)
        
        report_data.append({
            "asset": row.asset.upper(),
            "timestamp": row.timestamp,
            "predicted_price": round(row.predicted_price, 2),
            "actual_price": round(row.actual_price, 2),
            "accuracy": round(max(0, accuracy_val), 2)
        })

    return report_data

# ==========================================
# 2. إعادة تدريب النموذج (Model Retraining) - [متقدم]
# ==========================================
@router.post("/retrain")
async def trigger_retraining(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    تشغيل عملية تدريب الذكاء الاصطناعي في الخلفية باستخدام البيانات الجديدة.
    يستخدم كافة السجلات التاريخية (125,000+) لزيادة الدقة.
    """
    # نستخدم BackgroundTasks لكي لا تتجمد واجهة المستخدم أثناء التدريب
    background_tasks.add_task(retrain_model_logic, db)
    
    return {
        "status": "started",
        "message": "Model retraining initiated. The system is learning from new market patterns."
    }



@router.get("/training-logs")
def get_training_logs(db: Session = Depends(get_db)):
    """جلب آخر 10 عمليات تدريب مخزنة في قاعدة البيانات"""
    logs = db.query(models.ModelLog).order_by(models.ModelLog.trained_at.desc()).limit(10).all()
    return logs