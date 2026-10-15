"""
Archetype A: RemoteOK Public API Scraper (SRC-0035)
Docs / Endpoint: https://remoteok.com/api
"""
from typing import List, Optional
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("RemoteOKScraper")


class RemoteOKScraper(BaseScraper):
    API_URL = "https://remoteok.com/api"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0035",
            source_name="RemoteOK",
            archetype="A",
            http_client=http_client
        )

    async def scrape(self, limit: Optional[int] = 50) -> List[StandardJobListing]:
        logger.info(f"[{self.source_id}] Fetching jobs from {self.API_URL}...")

        try:
            # RemoteOK requires specific User-Agent format to avoid bot block
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            raw_data = await self.http_client.get_json(self.API_URL, headers=headers)
        except Exception as e:
            logger.error(f"[{self.source_id}] Failed to fetch from RemoteOK: {e}")
            return []

        if not isinstance(raw_data, list):
            logger.warning(f"[{self.source_id}] Unexpected data format from RemoteOK")
            return []

        # The first element is usually metadata/legal info
        items = [x for x in raw_data if isinstance(x, dict) and "position" in x]
        if limit:
            items = items[:limit]

        listings: List[StandardJobListing] = []
        for item in items:
            try:
                title = item.get("position", "")
                company = item.get("company", "")
                apply_url = item.get("url", "")
                if not apply_url.startswith("http"):
                    apply_url = f"https://remoteok.com{apply_url}" if apply_url else ""

                if not title or not company or not apply_url:
                    continue

                sal_min_raw = item.get("salary_min")
                sal_max_raw = item.get("salary_max")
                salary_raw = None
                if sal_min_raw or sal_max_raw:
                    salary_raw = f"${sal_min_raw or 0} - ${sal_max_raw or 0} USD"
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(salary_raw)

                loc_raw = item.get("location", "Remote")
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)
                posted_date = JobNormalizer.normalize_date(item.get("epoch"))

                tags = item.get("tags", [])

                listing = StandardJobListing(
                    id=f"remoteok-{item.get('id', '')}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc,
                    is_remote=is_remote,
                    country=country,
                    city=city,
                    employment_type="full_time",
                    salary_raw=salary_raw,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency=currency,
                    description=item.get("description"),
                    skills=tags if isinstance(tags, list) else [],
                    posted_date=posted_date,
                    raw_payload={"remoteok_id": item.get("id")}
                )
                listings.append(listing)
            except Exception as ex:
                logger.debug(f"[{self.source_id}] Error parsing item: {ex}")
                continue

        logger.info(f"[{self.source_id}] Successfully parsed {len(listings)} listings from RemoteOK.")
        return listings
