import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------
# 🔹 تفعيل وضع الاختبار (مهم جدًا)
# -------------------------------------------------
os.environ["TESTING"] = "true"

from app.main import app
from app.db.session import Base, get_db

# -------------------------------------------------
# 🔹 رابط قاعدة بيانات الاختبار
# -------------------------------------------------
TEST_DATABASE_URL = "postgresql://test_user:test_pass@test-db:5432/test_db"
# -------------------------------------------------
# 🔹 إنشاء Engine خاص بالاختبار
# -------------------------------------------------
engine = create_engine(TEST_DATABASE_URL)

# -------------------------------------------------
# 🔹 Session خاصة بالاختبار
# -------------------------------------------------
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =====================================================
# 🔹 إنشاء / حذف الجداول مرة واحدة قبل وبعد كل الاختبارات
# =====================================================
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# =====================================================
# 🔹 Session DB لكل اختبار مع Rollback (النهائي)
# =====================================================
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    
    try:
        yield db
    finally:
        db.close()
        transaction.rollback() 
        connection.close()

# =====================================================
# 🔹 TestClient مع override للـ get_db (يجب أن يتم استخدامه في الاختبارات)
# =====================================================
# ملاحظة: سنحتفظ بـ TestClient هنا، لكننا سنعدل test_auth.py لاستخدام AsyncClient 
# مع التبعية المتجاوزة التي تضمن الـ Rollback.
@pytest.fixture
def client(db):
    def override_get_db():
        # هذه الدالة تستخدم الجلسة 'db' التي تم إعدادها بالـ Rollback
        yield db

    # 1. تطبيق التجاوز
    app.dependency_overrides[get_db] = override_get_db

    # 2. تشغيل التطبيق (TestClient غير ضروري لاختبارات AsyncClient، 
    # لكن نحتاجه لتطبيق التجاوز)
    with TestClient(app) as c:
        yield c

    # 3. إزالة التجاوز بعد الانتهاء
    app.dependency_overrides.clear()
    