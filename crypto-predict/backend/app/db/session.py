from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

# 🔹 تحميل الإعدادات من config.py
settings = get_settings()

# 🔹 إنشاء محرك الاتصال بقاعدة البيانات
engine = create_engine(settings.DATABASE_URL, echo=True)

# 🔹 إنشاء جلسة اتصال SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🔹 تعريف Base class التي ستُستخدم لاحقًا في models.py
Base = declarative_base()


# 🔹 دالة للحصول على جلسة جديدة في أي مكان داخل المشروع
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
