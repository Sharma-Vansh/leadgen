"""
Archetype A: CryptoJobs.com Blockchain Jobs Adapter (SRC-0075)
Docs / Endpoint: https://www.cryptojobs.com/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("CryptoJobsScraper")


class CryptoJobsScraper(BaseScraper):
    BASE_URL = "https://www.cryptojobs.com"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0075",
            source_name="CryptoJobs",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching blockchain jobs from {self.BASE_URL}...")

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            res = await self.http_client.get(self.BASE_URL, headers=headers)
            html = res.text
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from CryptoJobs: {e}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        listings: List[StandardJobListing] = []
        seen_urls = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not "/job/" in href or href in seen_urls:
                continue
            seen_urls.add(href)

            try:
                title = a.text.strip()
                if not title or len(title) < 4:
                    continue

                apply_url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                card = a.find_parent("div") or a.find_parent("li")
                card_text = card.get_text(separator=" | ", strip=True) if card else ""

                parts = [p.strip() for p in card_text.split(" | ") if p.strip()]
                company = "Crypto Startup"
                if len(parts) > 1 and parts[1] != title:
                    company = parts[1]

                is_remote = "remote" in card_text.lower() or "remote" in title.lower()

                listing = StandardJobListing(
                    id=f"cj-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Remote" if is_remote else "Global",
                    is_remote=is_remote,
                    employment_type="full_time",
                    description=f"{title} at {company} in the Web3 ecosystem. {card_text[:250]}",
                    skills=["Web3", "Blockchain", "Solidity", "Crypto"],
                    raw_payload={"raw_title": title, "raw_company": company}
                )
                listings.append(listing)

                if limit and len(listings) >= limit:
                    break

            except Exception as e:
                logger.debug(f"[{self.source_id}] Skipping unparseable card: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs from CryptoJobs.")
        return listings
