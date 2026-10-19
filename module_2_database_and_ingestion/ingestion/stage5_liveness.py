"""
Stage 5: Listing Liveness and Expiration Service
Verifies URL availability using low-overhead asynchronous HEAD/GET requests.
Safely marks dead listings (404/410) as 'expired' without false positives on 403/429/5xx.
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from module_2_database_and_ingestion.config import settings
from module_2_database_and_ingestion.db.models import Job

logger = logging.getLogger("Stage5Liveness")


class LivenessCheckResult:
    def __init__(self):
        self.checked: int = 0
        self.active: int = 0
        self.expired: int = 0
        self.transient_errors: int = 0


class Stage5LivenessService:
    """Checks URL reachability and marks expired job postings."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    @classmethod
    async def check_url(
        cls,
        client: httpx.AsyncClient,
        url: str
    ) -> Tuple[bool, int, Optional[str]]:
        """
        Issues async HEAD request with GET fallback.
        Returns: (is_alive: bool, status_code: int, error_reason: Optional[str])
        """
        try:
            # 1. Try low-overhead HEAD request
            response = await client.head(url, headers=cls.HEADERS, follow_redirects=True)
            
            # If server blocks HEAD with 405 Method Not Allowed, try GET
            if response.status_code == 405:
                response = await client.get(url, headers=cls.HEADERS, follow_redirects=True)

            code = response.status_code

            # 404 Not Found or 410 Gone indicates listing was closed/deleted
            if code in (404, 410):
                return False, code, f"HTTP {code} Confirmed Dead Link"

            # 2xx and 3xx are definitely alive
            if 200 <= code < 400:
                return True, code, None

            # 403 Forbidden, 429 Too Many Requests, or 5xx Server Error:
            # DO NOT mark as expired; treat as transient rate-limit or firewall block
            return True, code, f"HTTP {code} Transient Anti-Bot / Gateway State"

        except httpx.TimeoutException:
            # Network timeout -> do not prematurely expire
            return True, 408, "Request Timeout (Transient)"
        except Exception as e:
            # Connection reset / DNS failure -> treat as transient
            return True, 500, f"Network Error ({type(e).__name__})"

    @classmethod
    async def verify_job_batch(
        cls,
        session: AsyncSession,
        jobs: List[Job],
        concurrency: int = 10
    ) -> LivenessCheckResult:
        """
        Checks a list of jobs concurrently and updates status in the database.
        """
        result = LivenessCheckResult()
        semaphore = asyncio.Semaphore(concurrency)
        timeout = httpx.Timeout(settings.HTTP_TIMEOUT_SECONDS)

        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            async def check_single_job(job: Job):
                async with semaphore:
                    result.checked += 1
                    is_alive, code, reason = await cls.check_url(client, job.apply_url)

                    if not is_alive:
                        job.status = "expired"
                        job.updated_at = datetime.now(timezone.utc)
                        result.expired += 1
                        logger.info(f"[Stage5Liveness] Expired Job {job.id} ('{job.title}'): {reason}")
                    elif reason:
                        result.transient_errors += 1
                    else:
                        result.active += 1

            tasks = [check_single_job(j) for j in jobs]
            await asyncio.gather(*tasks)

        await session.flush()
        return result
