from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache

# تحديد مسار المجلد الرئيسي
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # المتغيرات الأساسية
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REDIS_URL: str = None
    ENV: str = "development"

    # إعدادات Pydantic v2 للتعامل مع ملف .env وتجاهل الزيادات
    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        extra="ignore"  # هذا السطر سيجعل الباك إند يتجاهل المتغيرات الزائدة ويعمل فوراً
    )

@lru_cache()
def get_settings():
    return Settings()