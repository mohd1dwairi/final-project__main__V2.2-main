#يجب أن يتطابق مع التصميم المنطقي في صفحة 14 (يحتوي على predicted_value و status).
from pydantic import BaseModel
from datetime import datetime



class PredictionBase(BaseModel):
    asset: str
    timestamp: datetime
    predicted_price: float
    model_used: str
    confidence: float | None = None
    created_at: datetime

    class Config:
        orm_mode = True  # ضروري عشان يشتغل مع SQLAlchemy


class PredictionResponse(PredictionBase):
    id: int
