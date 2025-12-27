from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class SentimentBase(BaseModel):
    asset: str
    timestamp: datetime
    score: float
    label: str
    source: str
    source_url: Optional[str] = None
    meta: Optional[Dict] = None


class SentimentResponse(SentimentBase):
    id: int

    class Config:
        from_attributes = True
