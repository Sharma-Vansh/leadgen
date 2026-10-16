"""
Archetype C, Tier 1: SarkariResult Fast Track Table Scraper (SRC-0257)
Scrapes latest government and PSU recruitment notifications.
Target URL: https://www.sarkariresult.com/latestjob/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("SarkariResultScraper")


class SarkariResultScraper(BaseScraper):
    TARGET_URL = "https://www.sarkariresult.com/latestjob/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0257",
            source_name="SarkariResult",
            archetype="C",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest job notices from {self.TARGET_URL}...")

        try:
            resp = await self.http_client.get(self.TARGET_URL)
            soup = BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch page: {e}")
            return []

        # Find job list links inside #post or div containing list of a tags
        links = soup.select("#post a, #wrap a, ul li a")
        # Filter for genuine recruitment vacancy links
        EXCLUDE_KEYWORDS = [
            "admit card", "result", "answer key", "syllabus", "home", "contact",
            "scholarship", "terms", "condition", "privacy", "about us", "disclaimer",
            "certificate", "admission", "correction", "verification"
        ]
        
        job_links = []
        for a in links:
            href = a.get("href", "")
            title = a.get_text(strip=True)
            title_lower = title.lower()
            if href.startswith("http") and len(title) > 6:
                if not any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
                    # Check if it looks like a vacancy/job notification
                    if any(kw in title_lower for kw in ["recruitment", "online form", "apply", "vacancy", "post", "constable", "officer", "assistant", "clerk", "engineer", "trainee", "inter level", "apprentice", "staff"]):
                        job_links.append((title, href))

        if limit:
            job_links = job_links[:limit]

        listings: List[StandardJobListing] = []
        for idx, (title, href) in enumerate(job_links):
            try:
                # Detect conducting board (e.g. SSC, UPSC, Railway, BPSC, IBPS, Army, Police)
                title_upper = title.upper()
                board = "Govt of India / State PSU"
                for kw in ["SSC", "UPSC", "RRB", "RAILWAY", "IBPS", "BPSC", "UPPSC", "DSSSB", "ARMY", "NAVY", "AIR FORCE", "ISRO", "DRDO", "POLICE"]:
                    if kw in title_upper:
                        board = kw
                        break

                listing = StandardJobListing(
                    id=f"sarkariresult-{idx}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=f"Government ({board})",
                    apply_url=href,
                    location="India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    skills=["Government Job", board, "Civil Services / PSU"],
                    raw_payload={"board": board, "original_url": href}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} govt job listings.")
        return listings
