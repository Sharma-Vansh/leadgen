"""
Tier 2 Verifier: Official Application URL Verifier & Link Checker
"""
from typing import Tuple, Optional
import httpx
from module_1_scraping_engine.archetypes.archetype_c_govt_and_psu.verifiers.domain_whitelist import DomainWhitelistVerifier


class LinkChecker:
    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout

    async def verify_link(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Sends a HEAD request (fallback GET) to verify the destination link.
        Returns: (is_valid, final_url, error_message)
        """
        if not url or not url.startswith("http"):
            return False, None, "Invalid URL format"

        is_whitelisted = DomainWhitelistVerifier.is_official_govt_domain(url)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.head(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code >= 400:
                    # Some govt sites reject HEAD, try GET
                    resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})

                final_url = str(resp.url)
                if resp.status_code < 400:
                    return True, final_url, None
                else:
                    return False, final_url, f"HTTP Status {resp.status_code}"
        except Exception as e:
            # If server times out or blocks bot, return whitelist judgment
            if is_whitelisted:
                return True, url, f"Whitelisted domain (timeout bypassed): {e}"
            return False, url, str(e)
