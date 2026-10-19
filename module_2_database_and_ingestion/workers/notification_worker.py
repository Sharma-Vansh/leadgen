"""
Notification Worker
Scans application deadlines closing within 48–72 hours and dispatches email alerts via Resend API.
Maintains delivery history to guarantee idempotency and avoid duplicate spam.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Set
import logging
import httpx
from sqlalchemy import select

from module_2_database_and_ingestion.config import settings
from module_2_database_and_ingestion.workers.celery_app import app
from module_2_database_and_ingestion.db.session import get_async_session
from module_2_database_and_ingestion.db.models import Job

logger = logging.getLogger("NotificationWorker")

# In-memory delivery history to prevent duplicate alerts within the same service session
_DISPATCHED_ALERTS: Set[str] = set()


@app.task
def scan_upcoming_deadlines() -> Dict[str, Any]:
    """
    Scans for job listings with deadlines approaching in 48-72 hours.
    Dispatches notifications via Resend API if configured.
    """
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(hours=settings.DEADLINE_ALERT_HOURS_MIN)
    window_end = now + timedelta(hours=settings.DEADLINE_ALERT_HOURS_MAX)

    logger.info(
        f"[NotificationWorker] Scanning deadlines between "
        f"{window_start.strftime('%Y-%m-%d %H:%M')} and {window_end.strftime('%Y-%m-%d %H:%M')} UTC..."
    )

    async def _run():
        alerts_prepared = 0
        alerts_dispatched = 0

        async with get_async_session() as session:
            stmt = select(Job).where(
                Job.deadline >= window_start,
                Job.deadline <= window_end,
                Job.status != "expired"
            )
            result = await session.execute(stmt)
            upcoming_jobs = list(result.scalars().all())

            for job in upcoming_jobs:
                alert_key = f"{job.id}_{job.deadline.date() if job.deadline else 'none'}"
                if alert_key in _DISPATCHED_ALERTS:
                    continue  # Avoid duplicate notification

                alerts_prepared += 1
                hours_remaining = round((job.deadline - now).total_seconds() / 3600, 1) if job.deadline else 0

                payload = {
                    "job_id": job.id,
                    "title": job.title,
                    "company_name": job.company.name if job.company else "Direct Employer",
                    "deadline": job.deadline.isoformat() if job.deadline else None,
                    "hours_remaining": hours_remaining,
                    "apply_url": job.apply_url
                }

                # Dispatch via Resend API if API key is present
                if settings.RESEND_API_KEY:
                    try:
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            res = await client.post(
                                "https://api.resend.com/emails",
                                headers={
                                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "from": settings.NOTIFICATION_EMAIL_FROM,
                                    "to": ["student_subscribers@leadgen.dev"],  # Broadcast list or test sink
                                    "subject": f"Urgent: {job.title} application closes in {hours_remaining} hours!",
                                    "html": f"<p>Application for <b>{job.title}</b> is closing soon. Apply here: <a href='{job.apply_url}'>Apply</a></p>"
                                }
                            )
                            if res.status_code in (200, 201):
                                alerts_dispatched += 1
                                _DISPATCHED_ALERTS.add(alert_key)
                    except Exception as e:
                        logger.warning(f"[NotificationWorker] Failed to dispatch Resend email: {e}")
                else:
                    # In local / mock environment without live Resend key
                    logger.debug(f"[NotificationWorker] Mock Alert logged for Job {job.id} ({hours_remaining}h left)")
                    _DISPATCHED_ALERTS.add(alert_key)
                    alerts_dispatched += 1

        return {
            "window_hours": f"{settings.DEADLINE_ALERT_HOURS_MIN}-{settings.DEADLINE_ALERT_HOURS_MAX}",
            "alerts_prepared": alerts_prepared,
            "alerts_dispatched": alerts_dispatched
        }

    return asyncio.run(_run())
