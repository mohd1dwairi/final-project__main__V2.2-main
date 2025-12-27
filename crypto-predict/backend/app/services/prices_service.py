from datetime import datetime
import requests
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db import models

# تحسين الوظيفة لتجلب بيانات OHLCV حقيقية كما هو مطلوب في UC-06
def fetch_prices_from_api(asset_id: int, symbol: str, timeframe_id: int, timeframe_code: str, db: Session):
    """
    🪙 Fetch OHLCV data from Binance API (as specified in UC-06) 
    ✅ Map data to asset_id and timeframe_id from the Logical Design [cite: 266, 268]
    """
    
    # استخدام Binance للحصول على بيانات OHLCV كاملة (Open, High, Low, Close, Volume)
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}USDT&interval={timeframe_code}&limit=100"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    values = []
    for item in data:
        # تحويل الوقت من miliseconds إلى datetime
        ts = datetime.utcfromtimestamp(item[0] / 1000)

        values.append(
            {
                "asset_id": asset_id,        # ربط مع جدول CryptoAsset [cite: 266]
                "timeframe_id": timeframe_id, # ربط مع جدول Timeframe [cite: 268]
                "timestamp": ts,
                "open": float(item[1]),      # سعر الفتح [cite: 260]
                "high": float(item[2]),      # أعلى سعر [cite: 262]
                "low": float(item[3]),       # أدنى سعر [cite: 264]
                "close": float(item[4]),     # سعر الإغلاق [cite: 263]
                "volume": float(item[5]),    # الكمية [cite: 265]
            }
        )

    if not values:
        return 0

    # إدخال البيانات في جدول OHLCV_Candle (اسم الجدول من صفحة 14) 
    stmt = insert(models.OHLCV_Candle).values(values)

    # تجنب تكرار البيانات لنفس العملة والوقت والإطار الزمني
    stmt = stmt.on_conflict_do_nothing(
        index_elements=["asset_id", "timeframe_id", "timestamp"]
    )

    db.execute(stmt)
    db.commit()

    return len(values)