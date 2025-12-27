from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sentiment_schema import SentimentResponse
from app.services.sentiment_service import analyze_mock_sentiment
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])

@router.get("/{symbol}", response_model=list[SentimentResponse])
def get_sentiment(symbol: str,
                  db: Session = Depends(get_db),
                  current_user = Depends(get_current_user)):
    """
    تحليل مشاعر تجريبي باستخدام نصوص ثابتة (Mock)
    """
    return analyze_mock_sentiment(symbol, db)
