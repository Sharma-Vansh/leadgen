"""
Archetype C, Tier 1: India Govt Jobs Hub Scraper (SRC-0337)
Target URL: https://www.indgovtjobs.in/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("IndGovtJobsScraper")


class IndGovtJobsScraper(BaseScraper):
    TARGET_URL = "https://www.indgovtjobs.in/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0337",
            source_name="IndGovtJobs",
            archetype="C",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest job notices from {self.TARGET_URL}...")

        try:
            resp = await self.http_client.get(
                self.TARGET_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch page: {e}")
            return []

        EXCLUDE_KEYWORDS = [
            "admit card", "result", "answer key", "syllabus", "board exam", "admissions",
            "counseling", "merit list", "cutoff", "cut-off", "marks", "exam date", "home",
            "contact", "privacy", "disclaimer", "about us"
        ]

        # Posts are typically inside .post-title a or table td a
        links = soup.select(".post-title a, h2 a, .entry-title a, table tr td a")
        job_links = []
        for a in links:
            href = a.get("href", "")
            title = a.get_text(strip=True)
            title_lower = title.lower()
            if href.startswith("http") and len(title) > 8:
                if not any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
                    if any(kw in title_lower for kw in ["recruitment", "jobs", "vacancy", "post", "apply", "opening", "officer", "apprentice", "constable", "assistant"]):
                        job_links.append((title, href))

        # Deduplicate
        seen = set()
        unique_links = []
        for t, h in job_links:
            if h not in seen:
                seen.add(h)
                unique_links.append((t, h))

        if limit:
            unique_links = unique_links[:limit]

        listings: List[StandardJobListing] = []
        for idx, (title, href) in enumerate(unique_links):
            try:
                title_upper = title.upper()
                board = "Central / State Govt"
                for kw in ["SSC", "UPSC", "RRB", "RAILWAY", "BANK", "IBPS", "DRDO", "ISRO", "ARMY", "NAVY", "POLICE", "BEL", "BHEL", "NTPC", "ONGC"]:
                    if kw in title_upper:
                        board = kw
                        break

                listing = StandardJobListing(
                    id=f"indgovtjobs-{idx}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=f"Government ({board})",
                    apply_url=href,
                    location="India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    skills=["Government Job", board, "Recruitment Notification"],
                    raw_payload={"board": board, "original_url": href}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} govt job listings.")
        return listings
