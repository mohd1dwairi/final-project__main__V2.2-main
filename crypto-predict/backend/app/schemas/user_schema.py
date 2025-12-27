#عذا الملف يحدد شكل البيانات التي تدخل وتخرج من الـ API
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

# 1. المخطط الأساسي (يحتوي على البيانات المشتركة)
class UserBase(BaseModel):
    # استخدام User_Name وتحديد الطول الأقصى بـ 50 كما في التقرير 
    User_Name: str = Field(..., min_length=3, max_length=50) 
    # البريد الإلكتروني بحد أقصى 255 حرفاً 
    email: EmailStr = Field(..., max_length=255)

# 2. المخطط الخاص بعملية التسجيل (يُرسل من Frontend إلى Backend)
class UserCreate(UserBase):
    # كلمة المرور الخام التي يدخلها المستخدم في الواجهة (Main Course - Step 2) 
    password: str = Field(..., min_length=8)

# 3. المخطط الخاص باستجابة النظام (يُرسل من Backend إلى Frontend)
class UserResponse(UserBase):
    user_id: int # مطابق للمفتاح الأساسي في التقرير 
    created_at: date # مطابق لنوع البيانات Date في التقرير 

    class Config:
        # للسماح بقراءة البيانات من نماذج قاعدة البيانات (مثل SQLAlchemy)
        from_attributes = True


        # أضف هذا المخطط في نهاية ملف user_schema.py
class LoginRequest(BaseModel):
    email: EmailStr
    password: str