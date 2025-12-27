from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# إنشاء محرك قاعدة البيانات باستخدام الرابط من ملف .env
engine = create_engine(settings.DATABASE_URL)

# إنشاء جلسة للتعامل مع البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# التعريف الأساسي للجداول (Base) الذي سنرث منه في الموديلات
Base = declarative_base()

# دالة للحصول على الجلسة (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()