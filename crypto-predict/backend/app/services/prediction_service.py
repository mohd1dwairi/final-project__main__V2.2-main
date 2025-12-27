#يجب أن يحتوي على الوظيفة التي تستدعي نموذج الذكاء الاصطناعي (مثل LSTM) لمعالجة البيانات التاريخية وتوليد التوقع (UC-08).
from datetime import datetime, timedelta, timezone
from random import uniform
from sqlalchemy.orm import Session

from app.db import models
from app.db.models import User

def generate_mock_predictions(
    symbol: str,
    days: int,
    db: Session,
    user: User | None = None,
):
    """
    🔮 مولّد تنبؤات تجريبية (Mock)
    - لاحقًا يُستبدل بموديل ML حقيقي بدون تغيير الـ Router.
    """

    if days < 1:
        days = 1

    base_price = uniform(20000, 30000)
    predictions: list[models.Prediction] = []

    for i in range(1, days + 1):
        ts = datetime.now(timezone.utc) + timedelta(days=i)

        factor = 1 + uniform(-0.05, 0.05)
        predicted_price = base_price * factor

        confidence = uniform(0.8, 0.99)

        prediction = models.Prediction(
            asset=symbol.upper(),
            timestamp=ts,
            predicted_price=round(predicted_price, 2),
            model_used="mock_v1",
            confidence=round(confidence, 2),
            created_at=ts,
            created_by_user_id=user.id if user else None,
        )

        db.add(prediction)
        predictions.append(prediction)

    db.commit()
    return predictions
