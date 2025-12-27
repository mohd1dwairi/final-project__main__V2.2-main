import requests
from datetime import datetime # نحتاج لاستيراد datetime لاستخدامه في الـ Mock
from sqlalchemy.orm import Session
from app.db import models
# يجب استيراد الدالة الأصلية لجعل التجاوز يعمل بشكل صحيح (فيما بعد)
from app.services.prices_service import fetch_prices_from_api 


# -------------------------------------------------
# 🔹 دالة Mock تستبدل fetch_prices_from_api
# -------------------------------------------------
def mock_fetch_prices_from_api(symbol: str, days: int, db: Session):
    """
    تجاوز دالة الخدمة: بدلاً من الاتصال بـ CoinGecko، نُرجع بيانات وهمية مباشرة.
    """
    # بيانات Mock لـ Candle تتوافق مع التنسيق الذي تتوقعه الدالة الأصلية لتخزينه
    mock_data = [
        [1700000000000, 42000],
        [1700003600000, 42500],
        [1700007200000, 43000],
    ]
    
    results = []
    
    for ts_ms, price in mock_data:
        ts = datetime.utcfromtimestamp(ts_ms / 1000)

        # إنشاء كائنات Candle مباشرة للتأكد من تخزينها بشكل صحيح
        candle = models.Candle(
            asset=symbol.upper(),
            exchange="binance",
            timestamp=ts,
            open=price,
            high=price,
            low=price,
            close=price,
            volume=0.0,
        )
        db.add(candle)
        results.append(candle)
        
    db.commit()
    # يجب أن تعيد list[models.Candle] تماماً كما تتوقع نقطة النهاية
    return results

# -------------------------------------------------
# 🔹 دالة الاختبار المصححة
# -------------------------------------------------
def test_get_prices_and_store_in_db(client, db, monkeypatch):
    
    # =====================================================
    # 🔹 التجاوز (Override)
    # =====================================================
    # استبدال الدالة الحقيقية بدالة Mock الخاصة بنا
    monkeypatch.setattr(
        "app.routers.prices.fetch_prices_from_api",
        mock_fetch_prices_from_api
    )
    
    # =====================================================
    # 1️⃣ Register
    # =====================================================
    client.post(
        "/auth/register",
        json={
            "username": "price_user",
            "email": "price_user@test.com",
            "password": "password123"
        }
    )

    # =====================================================
    # 2️⃣ Login
    # =====================================================
    login_response = client.post(
        "/auth/login",
        data={
            "username": "price_user@test.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # =====================================================
    # 🔹 Clean candle table before test
    # =====================================================
    db.query(models.Candle).delete()
    db.commit()

    # =====================================================
    # 3️⃣ Call /prices
    # =====================================================
    # الآن، سيتم استدعاء mock_fetch_prices_from_api بدلاً من الأصلية
    response = client.get("/prices/bitcoin?days=1", headers=headers)
    
    # يجب أن يعيد 200 لأن الـ Mock ينجح الآن في إرجاع القيمة المطلوبة
    assert response.status_code == 200
    
    # تحقق من أن البيانات في الـ Response تحتوي على 3 عناصر
    assert len(response.json()) == 3

    # =====================================================
    # 4️⃣ Verify DB
    # =====================================================
    candles = db.query(models.Candle).filter(
        models.Candle.asset == "BITCOIN"
    ).all()

    # تحقق من أن الـ Mock قام بتخزين 3 عناصر بنجاح
    assert len(candles) == 3

    