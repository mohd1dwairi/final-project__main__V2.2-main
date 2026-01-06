from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user_schema import UserCreate, UserResponse, LoginRequest
from app.services.auth_service import register_user, login_user
from app.core.security import get_current_user
from app.db import models # استيراد الموديلات لجلب بيانات المستخدم

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(user_data, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        # 1. استدعاء خدمة تسجيل الدخول (التي تعيد التوكن كـ string حالياً)
        token = login_user(login_data.email, login_data.password, db)
        
        # 2. جلب بيانات المستخدم من قاعدة البيانات لإرسالها مع التوكن
        user = db.query(models.User).filter(models.User.email == login_data.email).first()
        
        if not user:
            raise ValueError("User not found")

        # 3. الحل: إعادة البيانات بشكل صحيح للفرونت إيند
        # هنا تأكدنا أننا لا نستخدم token["token"] لأن token هو مجرد نص
        return {
            "access_token": token, 
            "token_type": "bearer",
            "user": {
                "id": user.user_id,
                "name": user.User_Name,
                "role": user.role
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )