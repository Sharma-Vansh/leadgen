"""
Liveness Checker Worker
Scheduled Celery task that verifies active job links and expires dead postings.
"""
import asyncio
from typing import Dict, Any
import logging
from sqlalchemy import select

from module_2_database_and_ingestion.workers.celery_app import app
from module_2_database_and_ingestion.db.session import get_async_session
from module_2_database_and_ingestion.db.models import Job
from module_2_database_and_ingestion.ingestion.stage5_liveness import Stage5LivenessService, LivenessCheckResult

logger = logging.getLogger("LivenessWorker")


@app.task
def check_all_listings(limit: int = 200) -> Dict[str, Any]:
    """
    Scans active jobs and verifies their HTTP reachability.
    """
    logger.info(f"[LivenessWorker] Starting scheduled liveness check for up to {limit} active listings...")

    async def _run():
        async with get_async_session() as session:
            stmt = select(Job).where(Job.status != "expired").order_by(Job.updated_at.asc()).limit(limit)
            result = await session.execute(stmt)
            jobs = list(result.scalars().all())

            if not jobs:
                logger.info("[LivenessWorker] No active jobs found for health checking.")
                return {"checked": 0, "active": 0, "expired": 0, "transient_errors": 0}

            check_res: LivenessCheckResult = await Stage5LivenessService.verify_job_batch(
                session=session,
                jobs=jobs,
                concurrency=10
            )

            logger.info(
                f"[LivenessWorker] Checked {check_res.checked} jobs: "
                f"{check_res.active} active, {check_res.expired} expired, "
                f"{check_res.transient_errors} transient errors."
            )
            return {
                "checked": check_res.checked,
                "active": check_res.active,
                "expired": check_res.expired,
                "transient_errors": check_res.transient_errors
            }

    return asyncio.run(_run())
