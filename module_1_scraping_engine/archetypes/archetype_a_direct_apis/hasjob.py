"""
Archetype A: Hasjob Indian Startup Jobs Feed Scraper (SRC-0059)
Docs / Endpoint: https://hasjob.co/feed
"""
from typing import List, Optional
import logging
import feedparser
from bs4 import BeautifulSoup
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("HasjobScraper")


class HasjobScraper(BaseScraper):
    FEED_URL = "https://hasjob.co/feed"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0059",
            source_name="Hasjob",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching Indian startup jobs from {self.FEED_URL}...")

        try:
            # Fetch via async http client with realistic User-Agent
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            xml_text = await self.http_client.get(self.FEED_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch Hasjob feed: {e}")
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

                # Parse company name from entry summary or URL
                company = ""
                content_html = ""
                if entry.get("content"):
                    content_html = entry.get("content")[0].get("value", "")
                elif entry.get("summary"):
                    content_html = entry.get("summary", "")

                if content_html:
                    soup = BeautifulSoup(content_html, "html.parser")
                    strong_tag = soup.find("strong")
                    if strong_tag and strong_tag.text.strip():
                        company = strong_tag.text.strip()

                if not company:
                    parts = apply_url.replace("https://hasjob.co/", "").split("/")
                    if parts:
                        company = parts[0].replace(".com", "").replace("-", " ").title()

                loc_raw = entry.get("location", "India")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                if not country:
                    country = "India"

                published_date = JobNormalizer.normalize_date(entry.get("published") or entry.get("updated"))

                listing = StandardJobListing(
                    id=f"hasjob-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company or "Startup / Tech",
                    apply_url=apply_url,
                    location=loc or "India",
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    posted_at=published_date,
                    description=content_html,
                    tags=["Tech", "Startup", "India"],
                    raw_data={
                        "hasjob_id": entry.get("id"),
                        "raw_location": loc_raw
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings
