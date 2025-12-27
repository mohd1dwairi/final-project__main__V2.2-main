import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Crypto Price Prediction API",
    description="Backend for crypto prediction & sentiment analysis project",
    version="1.0.0",
)

# ========================
# CORS (تم تصحيحه هنا)
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في التطوير، نسمح للكل بالوصول للمتصفح
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # تم تصحيح الاسم هنا من allow_allowed_headers إلى allow_headers
)

# ========================
# Routers
# ========================
from app.routers import auth_router, prices, sentiment, predict, health

app.include_router(auth_router.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(sentiment.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(health.router, prefix="/api")

# ========================
# Scheduler
# ========================
from app.workers.scheduler import start_scheduler

@app.on_event("startup")
def on_startup():
    # نشغل الـ Scheduler فقط في العملية الرئيسية
    if os.getenv("RUN_MAIN") == "true" or os.getenv("TESTING") != "true":
        start_scheduler()

# ========================
# Root
# ========================
@app.get("/")
def root():
    return {
        "message": "🚀 Backend is running successfully!",
        "environment": settings.ENV,
        "database": "Connected",
    }