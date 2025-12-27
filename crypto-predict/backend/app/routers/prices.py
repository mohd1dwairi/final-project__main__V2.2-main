from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.candle_schema import CandleResponse
from app.core.security import get_current_user
from app.services.prices_service import fetch_prices_from_api
from app.db import models

router = APIRouter(prefix="/prices", tags=["Prices"])

# جلب بيانات الشموع (UC-05 & UC-06)
@router.get("/{symbol}", response_model=list[CandleResponse])
def get_prices(
    symbol: str,
    timeframe: str = "1h", # الافتراضي ساعة واحدة كما في التقرير
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # شرط تسجيل الدخول (صفحة 6)
):
    """
    جلب بيانات OHLCV حقيقية من Binance وتخزينها/عرضها (UC-06)
    """
    # 1. البحث عن معرف العملة (asset_id) في القاعدة بناءً على الرمز
    asset = db.query(models.CryptoAsset).filter(models.CryptoAsset.symbol == symbol.upper()).first()
    if not asset:
        raise HTTPException(status_code=404, detail="العملة غير موجودة في النظام")

    # 2. البحث عن معرف الإطار الزمني (timeframe_id)
    tf = db.query(models.Timeframe).filter(models.Timeframe.code == timeframe).first()
    if not tf:
        raise HTTPException(status_code=400, detail="إطار زمني غير مدعوم")

    try:
        # 3. جلب البيانات من Binance وتحديث القاعدة (UC-06)
        fetch_prices_from_api(
            asset_id=asset.asset_id, 
            symbol=symbol, 
            timeframe_id=tf.timeframe_id, 
            timeframe_code=timeframe, 
            db=db
        )

        # 4. جلب البيانات المخزنة من جدول OHLCV_Candle (صفحة 14) لإرسالها للرسم البياني
        candles = db.query(models.OHLCV_Candle).filter(
            models.OHLCV_Candle.asset_id == asset.asset_id,
            models.OHLCV_Candle.timeframe_id == tf.timeframe_id
        ).order_by(models.OHLCV_Candle.timestamp.desc()).limit(100).all()

        return candles

    except Exception as e:
        # الاستثناء EX1 (صفحة 7): فشل جلب البيانات
        raise HTTPException(status_code=500, detail="Data temporarily unavailable")