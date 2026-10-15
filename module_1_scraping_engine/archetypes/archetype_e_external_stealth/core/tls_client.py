"""
Archetype E Stealth Toolkit: TLS / JA3 Impersonator
Uses curl_cffi with Chrome 124 TLS finger-printing to bypass Cloudflare & DataDome anti-bot walls.
"""
from typing import Optional, Dict, Any
import logging
from module_1_scraping_engine.archetypes.archetype_e_external_stealth.core.proxy_rotator import ProxyRotator

logger = logging.getLogger("StealthTLSClient")


class StealthTLSClient:
    def __init__(self, proxy_rotator: Optional[ProxyRotator] = None, impersonate: str = "chrome124"):
        self.impersonate = impersonate
        self.proxy_rotator = proxy_rotator or ProxyRotator()
        self._session = None

    async def get_session(self):
        try:
            from curl_cffi.requests import AsyncSession
            if self._session is None:
                self._session = AsyncSession(impersonate=self.impersonate)
            return self._session
        except ImportError:
            logger.warning("[StealthTLSClient] curl_cffi not installed; falling back to standard httpx client.")
            import httpx
            return httpx.AsyncClient(follow_redirects=True)

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 20
    ):
        proxy = self.proxy_rotator.get_proxy()
        session = await self.get_session()

        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        if headers:
            default_headers.update(headers)

        try:
            kwargs = {
                "headers": default_headers,
                "params": params,
                "timeout": timeout
            }
            if proxy:
                kwargs["proxy"] = proxy

            # curl_cffi session request
            resp = await session.get(url, **kwargs)
            if proxy:
                self.proxy_rotator.report_success(proxy)
            return resp
        except Exception as e:
            if proxy:
                self.proxy_rotator.report_failure(proxy)
            logger.error(f"[StealthTLSClient] Request to {url} failed: {e}")
            raise

    async def close(self):
        if self._session:
            try:
                await self._session.close()
            except Exception:
                pass
