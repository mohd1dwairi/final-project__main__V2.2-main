from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

# 1️⃣ المخطط الأساسي للبيانات (يحتوي على تفاصيل الشمعة فقط)
class CandleBase(BaseModel):
    # النوع datetime كما ورد في التقرير [cite: 259]
    timestamp: datetime
    symbol: str # رمز الأصل (مثل BTCUSD) [cite: 261]
    # دقة 18,8 للأسعار (Open, High, Low, Close) [cite: 260, 262, 263, 264]
    open: Decimal = Field(..., max_digits=18, decimal_places=8)
    high: Decimal = Field(..., max_digits=18, decimal_places=8)
    low: Decimal = Field(..., max_digits=18, decimal_places=8)
    close: Decimal = Field(..., max_digits=18, decimal_places=8)
    # دقة 20,8 للكمية (Volume) [cite: 265]
    volume: Decimal = Field(..., max_digits=20, decimal_places=8)

# 2️⃣ المخطط المستخدم عند جلب البيانات من قاعدة البيانات أو الـ API
class CandleResponse(CandleBase):
    # استخدام candle_id بدلاً من id 
    candle_id: int
    
    # إضافة روابط المفاتيح الأجنبية الموجودة في التقرير [cite: 266, 268]
    asset_id: int
    timeframe_id: int

    class Config:
        # للسماح بقراءة البيانات من SQLAlchemy Models
        from_attributes = True