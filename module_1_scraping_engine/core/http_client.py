"""
Async HTTP Client with User-Agent Rotation, Retry Logic, and Rate Limiting
"""
import random
import logging
from typing import Optional, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from module_1_scraping_engine.config import DEFAULT_TIMEOUT, USER_AGENTS
from module_1_scraping_engine.core.rate_limiter import DomainRateLimiter

logger = logging.getLogger("ScrapingHttpClient")


class ScrapingHttpClient:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.rate_limiter = DomainRateLimiter()
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                headers={"Accept": "application/json, text/html, application/xhtml+xml, */*"}
            )
        return self._client

    def _get_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError))
    )
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        await self.rate_limiter.acquire(url)
        client = await self.get_client()
        req_headers = self._get_headers(headers)

        response = await client.get(url, params=params, headers=req_headers)
        if response.status_code == 429:
            logger.warning(f"Rate limited by {url}, status code: 429")
            response.raise_for_status()
        return response

    async def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        response = await self.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
