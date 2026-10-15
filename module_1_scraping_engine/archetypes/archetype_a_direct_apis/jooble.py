"""
Archetype A: Jooble Global Job Aggregator API Adapter (SRC-0014)
Docs: https://jooble.org/api/about
"""
from typing import List, Optional
import os
import logging
from module_1_scraping_engine.core.base_adapter import BaseScraper
from module_1_scraping_engine.core.schema import StandardJobListing
from module_1_scraping_engine.pipelines.normalizer import JobNormalizer

logger = logging.getLogger("JoobleScraper")


class JoobleScraper(BaseScraper):
    BASE_URL = "https://jooble.org/api"

    def __init__(self, http_client=None):
        super().__init__(
            source_id="SRC-0014",
            source_name="Jooble",
            archetype="A",
            http_client=http_client
        )
        self.api_key = os.getenv("JOOBLE_API_KEY", "879eacdb-00ec-4ad4-afa6-b7b8017a9e15")

    async def scrape(self, limit: Optional[int] = 50, keywords: str = "software engineer", location: str = "India") -> List[StandardJobListing]:
        if not self.api_key:
            logger.warning(
                f"[{self.source_id}] Jooble API key (JOOBLE_API_KEY) not found in environment. "
                "Register free at https://jooble.org/api/about to enable live calls."
            )
            return []

        url = f"{self.BASE_URL}/{self.api_key}"
        payload = {
            "keywords": keywords,
            "location": location,
            "page": 1
        }
        logger.info(f"[{self.source_id}] Fetching from Jooble for '{keywords}' in '{location}'...")

        try:
            data = await self.http_client.post_json(url, json=payload)
        except Exception as e:
            logger.error(f"[{self.source_id}] Jooble request failed: {e}")
            return []

        jobs = data.get("jobs", []) if isinstance(data, dict) else []
        if limit:
            jobs = jobs[:limit]

        listings: List[StandardJobListing] = []
        for j in jobs:
            try:
                title = j.get("title", "")
                company = j.get("company", "Confidential")
                apply_url = j.get("link", "")
                if not title or not apply_url:
                    continue

                salary_raw = j.get("salary")
                sal_min, sal_max, currency = JobNormalizer.normalize_salary(salary_raw)
                loc_raw = j.get("location", location)
                loc, is_remote, country, city = JobNormalizer.normalize_location(loc_raw)

                listing = StandardJobListing(
                    id=f"jooble-{j.get('id', hash(apply_url))}",
                    source_id=self.source_id,
                    source_name=self.source_name,
                    title=title,
                    company=company,
                    apply_url=apply_url,
                    location=loc or location,
                    is_remote=is_remote,
                    country=country or "India",
                    city=city,
                    salary_min=sal_min,
                    salary_max=sal_max,
                    salary_currency=currency,
                    posted_at=JobNormalizer.normalize_date(j.get("updated")),
                    description=j.get("snippet"),
                    tags=["Tech", "Aggregator"],
                    raw_data=j
                )
                listings.append(listing)
            except Exception as e:
                logger.debug(f"[{self.source_id}] Error normalizing Jooble job: {e}")
                continue

        logger.info(f"[{self.source_id}] Extracted {len(listings)} jobs from Jooble.")
        return listings
