from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import logging
import os

from app.db.session import SessionLocal
from app.services.prices_service import fetch_prices_from_api
from app.services.sentiment_service import analyze_texts

logging.basicConfig(level=logging.INFO)


def scheduled_fetch_prices():
    """🔄 Job: جلب أسعار bitcoin وتخزينها في قاعدة البيانات"""
    db: Session = SessionLocal()
    try:
        logging.info("⏳ Running scheduled job: fetch prices")
        fetch_prices_from_api("bitcoin", days=1, db=db)
        logging.info("✔️ Prices updated successfully")
    except Exception as e:
        logging.error(f"❌ Error in fetch prices job: {e}")
    finally:
        db.close()


def scheduled_sentiment():
    """🧠 Job: تحليل مشاعر Mock لعملة bitcoin وتخزينها"""
    db: Session = SessionLocal()
    try:
        logging.info("⏳ Running scheduled job: sentiment analysis")

        mock_texts = [
            "Bitcoin is doing great!",
            "Some fear Bitcoin will fall.",
            "People are accumulating Bitcoin heavily.",
        ]

        analyze_texts("bitcoin", mock_texts, db)
        logging.info("✔️ Sentiment updated successfully")
    except Exception as e:
        logging.error(f"❌ Error in sentiment job: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    🚀 تشغيل الـ BackgroundScheduler
    ✅ يمنع تشغيله أكثر من مرة مع uvicorn --reload
    """

    # 🔒 هذا السطر هو الحل
    if os.environ.get("RUN_MAIN") != "true":
        logging.info("⏭ Scheduler not started (not main process)")
        return

    scheduler = BackgroundScheduler()

    # 🕒 كل 10 دقائق: جلب الأسعار
    scheduler.add_job(
        scheduled_fetch_prices,
        "interval",
        minutes=10,
        id="fetch_prices_job",
        replace_existing=True,
    )

    # 🕒 كل 30 دقيقة: تحليل المشاعر
    scheduler.add_job(
        scheduled_sentiment,
        "interval",
        minutes=30,
        id="sentiment_job",
        replace_existing=True,
    )

    scheduler.start()
    logging.info("🚀 Scheduler started successfully (single instance)")
