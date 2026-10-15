"""
Archetype E Stealth Toolkit: Residential IP Proxy Pool Manager
Rotates proxy endpoints, tracks error rates, and isolates banned IPs.
"""
import random
import time
from typing import List, Optional, Dict
import logging

logger = logging.getLogger("ProxyRotator")


class ProxyRotator:
    def __init__(self, proxy_list: Optional[List[str]] = None):
        # Format: http://user:pass@host:port or socks5://host:port
        self.proxies: List[str] = proxy_list or []
        self._failures: Dict[str, int] = {}
        self._last_used: Dict[str, float] = {}

    def add_proxy(self, proxy_url: str):
        if proxy_url not in self.proxies:
            self.proxies.append(proxy_url)
            self._failures[proxy_url] = 0

    def get_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None

        # Filter out proxies with > 5 consecutive failures
        active = [p for p in self.proxies if self._failures.get(p, 0) < 5]
        if not active:
            # Reset failures if all exhausted
            logger.warning("[ProxyRotator] All proxies failed threshold; resetting failure counters.")
            self._failures.clear()
            active = self.proxies

        # Least recently used selection
        chosen = min(active, key=lambda p: self._last_used.get(p, 0.0))
        self._last_used[chosen] = time.monotonic()
        return chosen

    def report_success(self, proxy_url: str):
        if proxy_url in self._failures:
            self._failures[proxy_url] = max(0, self._failures[proxy_url] - 1)

    def report_failure(self, proxy_url: str):
        if proxy_url in self.proxies:
            self._failures[proxy_url] = self._failures.get(proxy_url, 0) + 1
            logger.debug(f"[ProxyRotator] Proxy {proxy_url} failure count: {self._failures[proxy_url]}")
