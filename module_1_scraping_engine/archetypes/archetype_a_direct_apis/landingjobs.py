"""
Archetype A: Landing.jobs RSS / Feed Scraper (SRC-0056)
Docs / Endpoint: https://landing.jobs/feed
"""
from typing import List, Optional
import logging
import feedparser
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("LandingJobsScraper")


class LandingJobsScraper(BaseScraper):
    FEED_URL = "https://landing.jobs/feed"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0056",
            source_name="LandingJobs",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching tech jobs from {self.FEED_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            xml_text = await self.http_client.get(self.FEED_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch Landing.jobs feed: {e}")
            return []

        parsed = feedparser.parse(xml_text)
        entries = parsed.entries
        if limit:
            entries = entries[:limit]

        listings: List[StandardJobListing] = []
        for entry in entries:
            try:
                title = entry.get("title", "")
                apply_url = entry.get("link", "")
                if not title or not apply_url:
                    continue

                # Parse company name from URL / landing.jobs/at/{company}/...
                company = "Tech Company"
                if "/at/" in apply_url:
                    try:
                        company = apply_url.split("/at/")[1].split("/")[0].replace("-", " ").title()
                    except Exception:
                        pass

                published_date = JobNormalizer.normalize_date(entry.get("published") or entry.get("updated"))
                summary = entry.get("summary", "")

                listing = StandardJobListing(
                    id=f"landingjobs-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Europe / Remote",
                    is_remote=True,
                    employment_type="full_time",
                    posted_at=published_date,
                    description=summary,
                    tags=["Tech", "Europe", "Remote"],
                    raw_data={
                        "landing_id": entry.get("id")
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings
