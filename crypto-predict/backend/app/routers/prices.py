from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import io
from app.db.session import get_db
from app.db import models

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.post("/upload-csv")
async def upload_candles_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed.")

    try:
        # قراءة الملف بالكامل
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # تحويل أسماء الأعمدة لتطابق الموديل
        df = df.rename(columns={'open_time': 'timestamp', 'symbol': 'asset'})
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['asset'] = df['asset'].str.lower()

        # تحويل البيانات إلى قائمة قواميس (Batch Preparation)
        records = df[['asset', 'timestamp', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')
        for record in records:
            record['exchange'] = 'binance'

        # تنفيذ الإدخال الجماعي (أسرع بكثير من الحلقة)
        stmt = insert(models.Candle).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=['asset', 'exchange', 'timestamp'])
        
        result = db.execute(stmt)
        db.commit()

        return {
            "status": "success",
            "message": f"Bulk upload completed. Total records in file: {len(df)}"
        }

    except Exception as e:
        db.rollback()
        print(f"Error detail: {str(e)}") # سيظهر في الـ Terminal الخاص بك
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")