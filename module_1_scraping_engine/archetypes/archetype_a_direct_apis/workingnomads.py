"""
Archetype A: Working Nomads Public API Scraper (SRC-0042)
Docs / Endpoint: https://www.workingnomads.com/api/exposed_jobs/
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("WorkingNomadsScraper")


class WorkingNomadsScraper(BaseScraper):
    API_URL = "https://www.workingnomads.com/api/exposed_jobs/"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0042",
            source_name="WorkingNomads",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL}...")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            raw_data = await self.http_client.get_json(self.API_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from Working Nomads: {e}")
            return []

        if not isinstance(raw_data, list):
            logger.warning(f"[{self.source_id}] Unexpected data format from Working Nomads")
            return []

        items = raw_data
        if limit:
            items = items[:limit]

        listings: List[StandardJobListing] = []
        for item in items:
            try:
                title = item.get("title", "")
                company = item.get("company_name", "")
                apply_url = item.get("url", "")
                if not title or not company or not apply_url:
                    continue

                loc_raw = item.get("location", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                # Working Nomads is predominantly remote
                is_remote = True

                posted_date = JobNormalizer.normalize_date(item.get("pub_date"))

                tags_raw = item.get("tags")
                if isinstance(tags_raw, list):
                    tags = tags_raw
                elif isinstance(tags_raw, str):
                    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
                else:
                    tags = []

                cat = item.get("category_name")
                if cat and cat not in tags:
                    tags.append(cat)

                listing = StandardJobListing(
                    id=f"wn-{hash(apply_url)}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or "Remote",
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    posted_at=posted_date,
                    description=item.get("description"),
                    tags=tags,
                    raw_data={
                        "category": cat,
                        "location_raw": loc_raw
                    }
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing job: {e}")
                continue

        logger.info(f"[{self.source_id}] Successfully extracted {len(listings)} jobs.")
        return listings
