"""
Archetype A: WeWorkRemotely RSS Feed Scraper (SRC-0040)
Docs / Feed: https://weworkremotely.com/categories/remote-programming-jobs.rss
"""
from typing import List, Optional
import logging
import feedparser
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("WWRScraper")


class WeWorkRemotelyScraper(BaseScraper):
    FEED_URL = "https://weworkremotely.com/categories/remote-programming-jobs.rss"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0040",
            source_name="WeWorkRemotely",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching RSS feed from {self.FEED_URL}...")

        try:
            resp = await self.http_client.get(self.FEED_URL)
            feed = feedparser.parse(resp.text)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch/parse WWR feed: {e}")
            return []

        entries = feed.entries
        if limit:
            entries = entries[:limit]

        listings: List[StandardJobListing] = []
        for entry in entries:
            try:
                # WWR title format is typically: "CompanyName: Job Title"
                raw_title = entry.get("title", "")
                company = "Remote Company"
                title = raw_title
                if ":" in raw_title:
                    parts = raw_title.split(":", 1)
                    company = parts[0].strip()
                    title = parts[1].strip()

                apply_url = entry.get("link", "")
                if not title or not apply_url:
                    continue

                posted_date = JobNormalizer.normalize_date(entry.get("published"))

                listing = StandardJobListing(
                    id=f"wwr-{entry.get('id', apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Remote",
                    is_remote=True,
                    employment_type="full_time",
                    description=entry.get("summary", ""),
                    posted_date=posted_date,
                    raw_payload={"guid": entry.get("id")}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing entry: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully parsed {len(listings)} listings from WeWorkRemotely.")
        return listings
