"""
Archetype A: NoDesk Remote Jobs RSS Scraper (SRC-0052)
Docs / Endpoint: https://nodesk.co/remote-jobs/index.xml
"""
from typing import List, Optional
import logging
import feedparser
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("NoDeskScraper")


class NoDeskScraper(BaseScraper):
    FEED_URL = "https://nodesk.co/remote-jobs/index.xml"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0052",
            source_name="NoDesk",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching remote jobs from {self.FEED_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            xml_text = await self.http_client.get(self.FEED_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch NoDesk feed: {e}")
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

                # Pattern: "Role | Location at Company"
                if " at " in raw_title:
                    role_loc, company = raw_title.rsplit(" at ", 1)
                else:
                    role_loc, company = raw_title, "Global Remote"

                parts = [p.strip() for p in role_loc.split("|")]
                title = parts[0]
                loc_raw = " | ".join(parts[1:]) if len(parts) > 1 else "Remote"

                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                is_remote = True

                published_date = JobNormalizer.normalize_date(entry.get("published") or entry.get("updated"))

                listing = StandardJobListing(
                    id=f"nodesk-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company.strip(),
                    apply_url=apply_url,
                    location=loc or "Remote",
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    posted_at=published_date,
                    description=entry.get("summary"),
                    tags=["Remote", "Global"],
                    raw_data={
                        "raw_title": raw_title,
                        "raw_location": loc_raw
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings
