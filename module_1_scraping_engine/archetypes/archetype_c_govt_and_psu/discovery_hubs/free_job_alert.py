"""
Archetype C, Tier 1: FreeJobAlert Table Scraper (SRC-0258)
Target URL: https://www.freejobalert.com/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("FreeJobAlertScraper")


class FreeJobAlertScraper(BaseScraper):
    TARGET_URL = "https://www.freejobalert.com/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0258",
            source_name="FreeJobAlert",
            archetype="C",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest job notifications from {self.TARGET_URL}...")

        try:
            resp = await self.http_client.get(self.TARGET_URL)
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch page: {e}")
            return []

        EXCLUDE_KEYWORDS = [
            "admit card", "result", "answer key", "syllabus", "board exam", "admissions",
            "counseling", "merit list", "cutoff", "cut-off", "marks", "exam date"
        ]

        rows = soup.select("table tr, .latjn tr, ul.latjn li a")
        candidates = []
        for r in rows:
            a_tag = r.find("a") if hasattr(r, "find") else None
            if not a_tag and r.name == "a":
                a_tag = r
            if a_tag:
                href = a_tag.get("href", "")
                title = a_tag.get_text(strip=True)
                title_lower = title.lower()
                if href.startswith("http") and len(title) > 8:
                    if not any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
                        candidates.append((title, href))

        if limit:
            candidates = candidates[:limit]

        listings: List[StandardJobListing] = []
        for idx, (title, href) in enumerate(candidates):
            try:
                board = "Central / State Govt"
                for kw in ["SSC", "UPSC", "RRB", "BANK", "IBPS", "POLICE", "ARMY", "TEACHING"]:
                    if kw in title.upper():
                        board = kw
                        break

                listing = StandardJobListing(
                    id=f"fja-{idx}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=f"Government ({board})",
                    apply_url=href,
                    location="India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    skills=["Government Job", board],
                    raw_payload={"board": board, "original_url": href}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings
