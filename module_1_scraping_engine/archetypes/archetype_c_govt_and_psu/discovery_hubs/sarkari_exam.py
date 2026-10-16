"""
Archetype C, Tier 1: SarkariExam Hub Scraper (SRC-0259)
Target URL: https://www.sarkariexam.com/
"""
from typing import List, Optional
import logging
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing

logger = logging.getLogger("SarkariExamScraper")


class SarkariExamScraper(BaseScraper):
    TARGET_URL = "https://www.sarkariexam.com/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0259",
            source_name="SarkariExam",
            archetype="C",
            http_client=http_client
        )

    FALLBACK_URL = "https://sarkarijobfind.com/"

    async def scrape(self, limit: Optional[int] = 20) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching latest job notices from {self.TARGET_URL}...")

        soup = None
        try:
            resp = await self.http_client.get(
                self.TARGET_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
            else:
                logger.warning(f"[{self.source_id}] Primary URL returned {resp.status_code}. Using mirror {self.FALLBACK_URL}...")
        except Exception as e:
            logger.warning(f"[{self.source_id}] Failed primary fetch: {e}")

        if not soup:
            try:
                resp = await self.http_client.get(
                    self.FALLBACK_URL,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
            except Exception as e:
                logger.error(f"[{self.source_id}] Fallback mirror also failed: {e}")
                return []

        if not soup:
            return []

        # Find latest job posts links
        EXCLUDE_KEYWORDS = [
            "admit card", "result", "answer key", "syllabus", "board exam", "admissions",
            "counseling", "merit list", "cutoff", "cut-off", "marks", "exam date", "home",
            "contact", "privacy", "disclaimer"
        ]

        links = soup.select(".post-content a, #table-content a, .entry-content a, .post-box a, .content a, table a, ul li a")
        job_links = []
        for a in links:
            href = a.get("href", "")
            title = a.get_text(strip=True)
            title_lower = title.lower()
            if href.startswith("http") and len(title) > 8:
                if not any(ex in title_lower for ex in EXCLUDE_KEYWORDS):
                    if any(kw in title_lower for kw in ["recruitment", "online form", "form", "apply", "vacancy", "post", "constable", "officer", "assistant", "clerk", "engineer", "trainee", "inter level", "apprentice", "staff", "jobs", "bharti"]):
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
                board = "Govt of India / State PSU"
                for kw in ["SSC", "UPSC", "RRB", "RAILWAY", "IBPS", "BPSC", "UPPSC", "DSSSB", "ARMY", "NAVY", "AIR FORCE", "ISRO", "DRDO", "POLICE", "BANK"]:
                    if kw in title_upper:
                        board = kw
                        break

                listing = StandardJobListing(
                    id=f"sarkariexam-{idx}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=f"Government ({board})",
                    apply_url=href,
                    location="India",
                    is_remote=False,
                    country="India",
                    employment_type="full_time",
                    skills=["Government Job", board, "Recruitment"],
                    raw_payload={"board": board, "original_url": href}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} govt job listings.")
        return listings
