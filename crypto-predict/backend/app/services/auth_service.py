#3. ملف app/services/auth_service.py (المنطق البرمجي)
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas.user_schema import UserCreate
from passlib.context import CryptContext
from datetime import date, datetime, timedelta # تعديل نوع التاريخ
from jose import jwt
# استيراد الإعدادات
#



from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

# 🔐 تشفير كلمة المرور (متطلب غير وظيفي صفحة 3)
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ✅ التحقق من كلمة المرور
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# 🪪 إنشاء JWT Token (الخطوة 4 في UC-02 صفحة 5)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

# 📝 إنشاء مستخدم جديد (UC-01 صفحة 4)
def register_user(user_data: UserCreate, db: Session) -> User:
    # 1. التحقق من الإيميل (Alternate Course AC1)
    if db.query(User).filter(User.email == user_data.email).first():
        raise ValueError("Email already registered.")

    hashed_pw = hash_password(user_data.password)
    
    # 2. بناء كائن المستخدم بناءً على المسميات في التقرير (صفحة 14)
    new_user = User(
        User_Name=user_data.User_Name, # تعديل المسمى
        email=user_data.email,
        password_hash=hashed_pw,
        created_at=date.today() # استخدام date بدلاً من datetime
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 🔐 تسجيل الدخول (UC-02 صفحة 5)
def login_user(email: str, password: str, db: Session) -> str:
    # التحقق من المستخدم بناءً على الإيميل (Step 3 في Main Course)
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password.") # نص الخطأ مطابق لـ AC1 صفحة 5

    # توليد التوكن (Step 4 في Main Course)
    return create_access_token({"sub": user.email})