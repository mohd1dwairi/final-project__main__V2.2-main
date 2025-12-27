import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
# الاستيرادات للحصول على النماذج
from sqlalchemy.orm import Session 
from app.db import models 
from app.main import app
# ملاحظة: لن نستخدم db: Session مباشرة، لكن يجب أن نستوردها لتعريفها

# ----------------------------------------------------
# 1. اختبار تسجيل المستخدم (Register)
# ----------------------------------------------------

# 💡 نطلب 'client' لضمان تطبيق override get_db من conftest.py
@pytest.mark.asyncio
async def test_register_user(client): 
    # db: Session لم تعد موجودة في توقيع الدالة، لكنها موجودة ضمن client/override

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            response = await ac.post("/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            })
            
            # يمكنك إعادة سطر الطباعة إذا فشل بـ 400 لفحص JSON (للتأكد من الرسالة)
            # print(response.json())
            
            assert response.status_code == 200

# ----------------------------------------------------
# 2. اختبار تسجيل الدخول (Login)
# ----------------------------------------------------

# 💡 نطلب 'client' لضمان تطبيق override get_db من conftest.py
@pytest.mark.asyncio
async def test_login_user(client): 
    # 🔹 تم إزالة التنظيف اليدوي. ونعتمد على Rollback
    
    # 1. تسجيل مستخدم (لضمان وجوده عند محاولة تسجيل الدخول)
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # تسجيل المستخدم أولاً (يجب أن يعود بـ 200)
            reg_response = await ac.post("/auth/register", json={
                "username": "login_test_user",
                "email": "test@example.com",
                "password": "password123"
            })
            # هذا يجب أن ينجح الآن
            assert reg_response.status_code == 200
            
            # 2. محاولة تسجيل الدخول
            response = await ac.post("/auth/login", data={
                "username": "test@example.com",
                "password": "password123"
            })
            
            assert response.status_code == 200
            assert "access_token" in response.json()