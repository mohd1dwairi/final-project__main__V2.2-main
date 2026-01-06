from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# إنشاء محرك قاعدة البيانات
engine = create_engine(settings.DATABASE_URL)

# إعداد الجلسات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# التعريف الأساسي للموديلات
Base = declarative_base()

# دالة الحصول على قاعدة البيانات (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()