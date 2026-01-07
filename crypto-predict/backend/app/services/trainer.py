import pandas as pd
import numpy as np
import joblib
import os
from sqlalchemy.orm import Session
from xgboost import XGBRegressor
from datetime import datetime
from app.db import models

def retrain_model_logic(db: Session):
    """
    نسخة مطورة تشمل نظام تسجيل العمليات (Logging System).
    تقوم بتدريب الموديل وحفظ النتيجة في جدول model_logs.
    """
    # متغيرات لتتبع الحالة
    start_time = datetime.now()
    records_used = 0
    
    try:
        print(f"[{start_time}] Starting Model Retraining...")

        # 1. جلب البيانات (كما هي في كودك)
        candles = db.query(models.Candle).all()
        df_prices = pd.DataFrame([{'asset': c.asset, 'timestamp': c.timestamp, 'close': c.close, 'open': c.open, 'high': c.high, 'low': c.low, 'volume': c.volume} for c in candles])
        
        sentiments = db.query(models.Sentiment).all()
        df_sentiments = pd.DataFrame([{'asset': s.asset, 'timestamp': s.timestamp, 'sent_count': s.sent_count, 'avg_sentiment': s.avg_sentiment, 'pos_count': s.pos_count, 'neg_count': s.neg_count, 'neu_count': s.neu_count, 'pos_ratio': s.pos_ratio, 'neg_ratio': s.neg_ratio, 'neu_ratio': s.neu_ratio, 'has_news': s.has_news} for s in sentiments])

        if df_prices.empty or df_sentiments.empty:
            raise Exception("Database tables are empty. Cannot train model.")

        # 2. دمج البيانات ومعالجة الأهداف
        df_total = pd.merge(df_prices, df_sentiments, on=['asset', 'timestamp'], how='inner')
        records_used = len(df_total) # تخزين عدد السجلات للـ Log
        
        df_total['target'] = df_total.groupby('asset')['close'].shift(-1)
        df_total = df_total.dropna()

        # 3. التدريب والحفظ (استخدام الـ 14 خاصية)
        feature_cols = ["open", "high", "low", "close", "volume", "sent_count", "avg_sentiment", "pos_count", "neg_count", "neu_count", "pos_ratio", "neg_ratio", "neu_ratio", "has_news"]
        X = df_total[feature_cols]
        y = df_total['target']

        model = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42)
        model.fit(X, y)

        model_path = "app/models/latest_model.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)

        # --- 4. تسجيل نجاح العملية في قاعدة البيانات ---
        new_log = models.ModelLog(
            trained_at=start_time,
            records_count=records_used,
            status="Success"
        )
        db.add(new_log)
        db.commit()
        
        print(f"✅ Success: Model retrained on {records_used} records.")
        return True

    except Exception as e:
        db.rollback() # التراجع في حال حدوث خطأ أثناء التعامل مع الـ Database
        error_msg = str(e)
        
        # --- 5. تسجيل فشل العملية مع ذكر السبب ---
        fail_log = models.ModelLog(
            trained_at=start_time,
            records_count=records_used,
            status="Failed",
            error_message=error_msg[:500] # نأخذ أول 500 حرف فقط
        )
        db.add(fail_log)
        db.commit()
        
        print(f"❌ Error: {error_msg}")
        return False