"""
Token Bucket Rate Limiter per Domain
Ensures outgoing scraping requests do not exceed specified requests-per-second thresholds.
"""
import asyncio
import time
from typing import Dict
from urllib.parse import urlparse
from module_1_scraping_engine.config import DOMAIN_RATE_LIMITS


class DomainRateLimiter:
    def __init__(self):
        self._limits = DOMAIN_RATE_LIMITS
        self._last_call: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    def _extract_domain(self, url: str) -> str:
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc
        except Exception:
            return "default"

    async def acquire(self, url: str):
        domain = self._extract_domain(url)
        rate_limit = self._limits.get(domain, self._limits.get("default", 2.0))
        min_interval = 1.0 / max(rate_limit, 0.1)

        async with self._lock:
            now = time.monotonic()
            last_time = self._last_call.get(domain, 0.0)
            elapsed = now - last_time

            if elapsed < min_interval:
                sleep_needed = min_interval - elapsed
                await asyncio.sleep(sleep_needed)
                now = time.monotonic()

            self._last_call[domain] = now
