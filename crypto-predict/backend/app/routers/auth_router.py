#هذا الملف هو "نقطة التماس" التي سيخاطبها الـ Frontend (React) لإتمام عمليتي التسجيل وتسجيل الدخول.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import UserCreate, UserResponse, LoginRequest # سنحتاج LoginRequest
from app.services.auth_service import register_user, login_user
from app.core.security import get_current_user
from app.db.models import User

# تغيير التسمية لتطابق التقرير
router = APIRouter(prefix="/auth", tags=["Authentication"])

# 1️⃣ تسجيل حساب جديد (UC-01)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(user_data, db)
    except ValueError as e:
        # رسالة الخطأ: "Email already registered" (AC1 صفحة 4)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # رسالة الخطأ: "System error, please try again later" (EX1 صفحة 4)
        raise HTTPException(status_code=500, detail="System error, please try again later.")

# 2️⃣ تسجيل الدخول (UC-02)
# التعديل: استخدام JSON body بدلاً من Form وتغيير username إلى email
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        # التقرير يطلب الإيميل وكلمة المرور (Step 1 صفحة 5)
        token = login_user(login_data.email, login_data.password, db)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        # رسالة الخطأ: "Invalid email or password" (AC1 صفحة 5)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

# 3️⃣ الحصول على بيانات المستخدم الحالي (اختياري للربط مع Dashboard)
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user