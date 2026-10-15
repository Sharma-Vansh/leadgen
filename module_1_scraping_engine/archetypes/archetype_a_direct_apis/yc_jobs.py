"""
Archetype A: Y Combinator & Hacker News Jobs Public API Adapter (SRC-0047)
Docs / Endpoint: https://hacker-news.firebaseio.com/v0/jobstories.json
"""
from typing import List, Optional
import logging
from datetime import datetime
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("YCJobsScraper")


class YCJobsScraper(BaseScraper):
    API_URL = "https://hacker-news.firebaseio.com/v0/jobstories.json"
    ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0047",
            source_name="YCombinator",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Y Combinator startup jobs from {self.API_URL}...")

        try:
            job_ids = await self.http_client.get_json(self.API_URL)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch job IDs: {e}")
            return []

        if not isinstance(job_ids, list):
            return []

        if limit:
            job_ids = job_ids[:limit]

        listings: List[StandardJobListing] = []
        for j_id in job_ids:
            try:
                item_url = self.ITEM_URL.format(item_id=j_id)
                item = await self.http_client.get_json(item_url)
                if not item or not isinstance(item, dict):
                    continue

                raw_title = item.get("title", "")
                apply_url = item.get("url") or f"https://news.ycombinator.com/item?id={j_id}"
                if not raw_title:
                    continue

                # Parse company name from title: e.g. "PostEra (YC W20) Is Hiring AI Researchers"
                company = "YC Startup"
                title = raw_title
                if " is hiring " in raw_title.lower():
                    parts = raw_title.split(" is hiring ", 1) if " is hiring " in raw_title else raw_title.split(" Is Hiring ", 1)
                    if len(parts) == 2:
                        company = parts[0].strip()
                        title = parts[1].strip()

                time_val = item.get("time")
                posted_date = datetime.utcfromtimestamp(float(time_val)).isoformat() if time_val else None

                listing = StandardJobListing(
                    id=f"yc-{j_id}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location="Remote / Global",
                    is_remote=True,
                    employment_type="full_time",
                    posted_at=posted_date,
                    description=item.get("text") or raw_title,
                    tags=["YC", "Startup", "Tech"],
                    raw_data=item
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing YC job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} YC jobs.")
        return listings
