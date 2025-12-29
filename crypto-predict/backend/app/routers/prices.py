from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert # استيراد هام جداً لمعالجة التكرار
import pandas as pd
import io
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.post("/upload-csv")
async def upload_candles_csv(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="يرجى رفع ملف بصيغة CSV فقط")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # 1. توحيد أسماء الأعمدة
        if 'open_time' in df.columns:
            df = df.rename(columns={'open_time': 'timestamp'})
        
        # تحويل التوقيت لصيغة صحيحة
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        success_count = 0
        for _, row in df.iterrows():
            # 2. بناء استعلام إدخال متطور (PostgreSQL Upsert)
            stmt = insert(models.Candle).values(
                asset=str(row['symbol']).lower(),
                timestamp=row['timestamp'],
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume']),
                exchange="binance"
            )

            # 3. الحل الجذري: إذا حدث تكرار في (asset, exchange, timestamp) لا تفعل شيئاً (تجاهل الخطأ)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['asset', 'exchange', 'timestamp']
            )
            
            result = db.execute(stmt)
            if result.rowcount > 0: # إذا تم الإدخال فعلياً (وليس تجاهله)
                success_count += 1
        
        db.commit()
        return {"status": "success", "message": f"تمت معالجة الملف بنجاح. تم إدخال {success_count} سجل جديد وتجاهل المكرر."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطأ تقني: {str(e)}")