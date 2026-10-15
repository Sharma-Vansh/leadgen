"""
Archetype D, Tier 2: Link Resolver and Unshortener
Extracts application URLs, Google Forms, Typeform links, and unshortens bit.ly/tinyurl.
"""
import re
from typing import List, Optional
import httpx


class LinkUnshortener:
    URL_REGEX = re.compile(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    )

    SHORTENER_DOMAINS = ["bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rb.gy", "linktr.ee"]

    def extract_urls(self, text: str) -> List[str]:
        if not text:
            return []
        return self.URL_REGEX.findall(text)

    async def unshorten_url(self, url: str, timeout: float = 6.0) -> str:
        """
        Unshortens redirect links (bit.ly, etc.) to get the canonical destination URL.
        """
        if not any(short in url for short in self.SHORTENER_DOMAINS):
            return url

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                resp = await client.head(url, headers={"User-Agent": "Mozilla/5.0"})
                return str(resp.url)
        except Exception:
            return url
