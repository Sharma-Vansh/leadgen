"""
Archetype A: Python Software Foundation Jobs RSS Adapter (SRC-0048)
Docs / Endpoint: https://www.python.org/jobs/feed/rss/
"""
from typing import List, Optional
import logging
import feedparser
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("PythonOrgScraper")


class PythonOrgScraper(BaseScraper):
    FEED_URL = "https://www.python.org/jobs/feed/rss/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0048",
            source_name="PythonOrg",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Python engineering jobs from {self.FEED_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            xml_text = await self.http_client.get(self.FEED_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch Python.org feed: {e}")
            return []

        parsed = feedparser.parse(xml_text)
        entries = parsed.entries
        if limit:
            entries = entries[:limit]

        listings: List[StandardJobListing] = []
        for entry in entries:
            try:
                raw_title = entry.get("title", "")
                apply_url = entry.get("link", "")
                if not raw_title or not apply_url:
                    continue

                # Pattern: "Software Engineer - Full Stack, 3Gimbals"
                if ", " in raw_title:
                    title, company = raw_title.rsplit(", ", 1)
                else:
                    title, company = raw_title, "Python Employer"

                published_date = JobNormalizer.normalize_date(entry.get("published") or entry.get("updated"))
                summary = entry.get("summary", "")

                listing = StandardJobListing(
                    id=f"pyorg-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title.strip(),
                    company=company.strip(),
                    apply_url=apply_url,
                    location="Remote / Global",
                    is_remote=True,
                    employment_type="full_time",
                    posted_at=published_date,
                    description=summary,
                    tags=["Python", "Software Engineering", "Tech"],
                    raw_data={
                        "raw_title": raw_title
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Python.org job: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from Python.org.")
        return listings
