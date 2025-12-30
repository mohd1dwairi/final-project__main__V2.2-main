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
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        # ربط مسميات ملفك بأسماء الجدول
        df = df.rename(columns={'open_time': 'timestamp', 'symbol': 'asset'})
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['asset'] = df['asset'].str.lower()

        # تجهيز البيانات للرفع الجماعي
        records = df[['asset', 'timestamp', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')
        for record in records:
            record['exchange'] = 'binance'

        # تنفيذ الإدخال
        stmt = insert(models.Candle).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=['asset', 'exchange', 'timestamp'])
        
        db.execute(stmt)
        db.commit()

        return {"status": "success", "message": f"Uploaded {len(df)} records successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))