"""
Celery Application & Beat Schedule Configuration
Initializes Celery instance with Redis broker and schedules periodic workers.
"""
import os
from celery import Celery
from celery.schedules import crontab
from module_2_database_and_ingestion.config import settings

# Initialize Celery
app = Celery("leadgen_ingestion")

# Configure Celery with settings
app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    worker_prefetch_multiplier=1,
    task_routes={
        "module_2_database_and_ingestion.workers.ingestion_worker.*": {"queue": "ingestion_queue"},
        "module_2_database_and_ingestion.workers.liveness_checker.*": {"queue": "maintenance_queue"},
        "module_2_database_and_ingestion.workers.notification_worker.*": {"queue": "notification_queue"}
    },
    beat_schedule={
        # 1. 24-Hour Listing Liveness Check (Daily at 02:00 AM UTC)
        "daily-liveness-check": {
            "task": "module_2_database_and_ingestion.workers.liveness_checker.check_all_listings",
            "schedule": crontab(hour=2, minute=0),
            "options": {"queue": "maintenance_queue"}
        },
        # 2. Upcoming Deadline Alerts (Every 4 hours)
        "scan-deadlines-every-4h": {
            "task": "module_2_database_and_ingestion.workers.notification_worker.scan_upcoming_deadlines",
            "schedule": crontab(minute=0, hour="*/4"),
            "options": {"queue": "notification_queue"}
        }
    }
)

# Auto-discover tasks in workers package
app.autodiscover_tasks([
    "module_2_database_and_ingestion.workers.ingestion_worker",
    "module_2_database_and_ingestion.workers.liveness_checker",
    "module_2_database_and_ingestion.workers.notification_worker"
])
